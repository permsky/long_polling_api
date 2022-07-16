import logging
import os
import textwrap
import time
from typing import Optional

import requests
import telegram
from dotenv import load_dotenv
from loguru import logger


class TelegramLogsHandler(logging.Handler):
    """Custom handler for sending logs in Telegram bot."""
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        formatter = logging.Formatter("%(message)s")
        message = formatter.format(record)
        message_chunks = message.split("|")[2:]
        chunk_0 = message_chunks[0].split("-")[1:]
        message_chunks[0] = "-".join(chunk_0)
        text = "|".join(message_chunks)
        self.tg_bot.send_message(chat_id=self.chat_id, text=text)


def notify(
    token: Optional[str],
    chat_id: Optional[str],
    user_reviews: dict
) -> None:
    """Send notification in telegram chat."""
    last_attempt = user_reviews["new_attempts"][0]
    result = """
    Преподавателю все понравилось, можно приступать к следующему уроку!
    """
    if last_attempt["is_negative"]:
        result = "К сожалению, в работе нашлись ошибки."
    message_text = textwrap.dedent(f"""\
    У вас проверили работу\
    [{last_attempt["lesson_title"]}]({last_attempt["lesson_url"]})
    {result}
    """
    )
    bot = telegram.Bot(token)
    bot.send_message(
        chat_id=chat_id,
        text=message_text,
        parse_mode="Markdown"
    )


@logger.catch
def main() -> None:
    """Dealing with long polling API devman.org."""
    load_dotenv()
    url = "https://dvmn.org/api/long_polling/"
    dvmn_token = os.getenv("DEVMAN_TOKEN")
    tg_token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    headers = {"Authorization": f"Token {dvmn_token}"}
    params = dict()
    connection_errors_count = 0
    waiting_time = 0
    tg_bot = telegram.Bot(tg_token)
    logger.add(TelegramLogsHandler(tg_bot, chat_id))
    logger.info("Бот запущен")

    while True:
        try:
            time.sleep(waiting_time)
            response = requests.get(
                url=url, headers=headers, params=params, timeout=100
            )
            response.raise_for_status()
            user_reviews = response.json()
            if user_reviews["status"] == "found":
                notify(
                    token=tg_token,
                    chat_id=chat_id,
                    user_reviews=user_reviews
                )
                params = {"timestamp": user_reviews["last_attempt_timestamp"]}
            connection_errors_count = 0
            waiting_time = 0
            if user_reviews["status"] == "timeout":
                params = {"timestamp": user_reviews["timestamp_to_request"]}
        except requests.exceptions.ReadTimeout as err:
            logger.exception("Бот упал с ошибкой:")
        except requests.exceptions.ConnectionError as err:
            logger.exception("Бот упал с ошибкой:")
            connection_errors_count += 1
            logger.info(f"connection errors count: {connection_errors_count}")
            if connection_errors_count > 5:
                waiting_time = 60
        except Exception as err:
            logger.exception("Бот упал с ошибкой:")


if __name__ == "__main__":
    main()
