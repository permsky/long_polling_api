import os
import sys

import requests
import telegram

from dotenv import load_dotenv
from loguru import logger


def notify(
        token: str,
        chat_id: int,
        user_reviews: dict) -> None:
    '''Send notification in telegram chat.'''
    last_attempt = user_reviews['new_attempts'][0]
    result = '''
    Преподавателю все понравилось, можно приступать к следующему уроку!
    '''
    if last_attempt['is_negative']:
        result = 'К сожалению, в работе нашлись ошибки.'
    message_text = (
        f'У вас проверили работу [{last_attempt["lesson_title"]}]'
        f'({last_attempt["lesson_url"]})\n\n{result}'
    )
    bot = telegram.Bot(token)
    bot.send_message(
        chat_id=chat_id,
        text=message_text,
        parse_mode='Markdown'
    )


@logger.catch
def main() -> None:
    '''Dealing with long polling API devman.org.'''
    logger.add(
        sys.stderr,
        format='[{time:HH:mm:ss}] <lvl>{message}</lvl>',
        level='ERROR'
    )

    load_dotenv()
    url = 'https://dvmn.org/api/long_polling/'
    dvmn_token = os.getenv('DEVMAN_TOKEN')
    tg_token = os.getenv('TG_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    headers = {'Authorization': f'Token {dvmn_token}'}

    while True:
        try:
            response = requests.get(
                url=url,
                headers=headers
            )
            response.raise_for_status()
            user_reviews = response.json()
            if user_reviews['status'] == 'found':
                notify(
                    token=tg_token,
                    chat_id=chat_id,
                    user_reviews=user_reviews
                )
            if user_reviews['status'] == 'timeout':
                params = {'timestamp': user_reviews['timestamp_to_request']}
                response = requests.get(
                    url=url,
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                notify(
                    token=tg_token,
                    chat_id=chat_id,
                    response=response.json()
                )
                continue
        except requests.exceptions.ReadTimeout as err:
            logger.error(err)
        except ConnectionError as err:
            logger.error(err)


if __name__ == '__main__':
    main()
