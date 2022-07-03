import os
import sys
import textwrap
import time

from typing import Optional

import requests
import telegram

from dotenv import load_dotenv
from loguru import logger


def notify(token: Optional[str], chat_id: Optional[str], user_reviews: dict) -> None:
    """Send notification in telegram chat."""
    last_attempt = user_reviews["new_attempts"][0]
    result = """
    Преподавателю все понравилось, можно приступать к следующему уроку!
    """
    if last_attempt["is_negative"]:
        result = "К сожалению, в работе нашлись ошибки."
    message_text = textwrap.dedent(
        f"""\
    У вас проверили работу\
    [{last_attempt["lesson_title"]}]({last_attempt["lesson_url"]})

    {result}
    """
    )
    bot = telegram.Bot(str(token))
    bot.send_message(chat_id=chat_id, text=message_text, parse_mode="Markdown")


@logger.catch
def main() -> None:
    """Dealing with long polling API devman.org."""
    logger.add(
        sys.stderr, format="[{time:HH:mm:ss}] <lvl>{message}</lvl>", level="ERROR"
    )

    load_dotenv()
    url = "https://dvmn.org/api/long_polling/"
    dvmn_token = os.getenv("DEVMAN_TOKEN")
    tg_token = os.getenv("TG_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    headers = {"Authorization": f"Token {dvmn_token}"}
    params: dict = dict()
    connection_errors_count = 0
    waiting_time = 0

    while True:
        try:
            time.sleep(waiting_time)
            response = requests.get(
                url=url, headers=headers, params=params, timeout=100
            )
            response.raise_for_status()
            user_reviews = response.json()
            if user_reviews["status"] == "found":
                notify(token=tg_token, chat_id=chat_id, user_reviews=user_reviews)
                params = {"timestamp": user_reviews["last_attempt_timestamp"]}
            connection_errors_count = 0
            waiting_time = 0
            if user_reviews["status"] == "timeout":
                params = {"timestamp": user_reviews["timestamp_to_request"]}
        except requests.exceptions.ReadTimeout as err:
            logger.error(err)
        except requests.exceptions.ConnectionError as err:
            logger.error(err)
            connection_errors_count += 1
            logger.info(f"connection errors count: {connection_errors_count}")
            if connection_errors_count > 5:
                waiting_time = 60


if __name__ == "__main__":
    main()
