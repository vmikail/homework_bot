import os
import time
import sys
import logging
import requests
import telegram
import exceptions

from typing import Dict
from http import HTTPStatus
from dotenv import load_dotenv


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s %(levelname)s '
                              '%(message)s %(name)s'
                              )
handler.setFormatter(formatter)


def send_message(bot, message):
    """Отправка сообщения."""
    logger.info('Отправка сообщения')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        raise Exception(f'Не удалось отправить сообщение: {error}')
    else:
        logger.info('сообщение отправлено')


def get_api_answer(current_timestamp):
    """Запрос к API."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except Exception as error:
        raise Exception(f'Ошбика в enpoint запросе: {error}')
    if response.status_code != HTTPStatus.OK:
        raise exceptions.APIResponseError('Неверный ответ API')
    try:
        response = response.json()
    except Exception as error:
        raise Exception(f'Ошибка получения json: {error}')
    return response


def check_response(response):
    """Проверка ответа API."""
    homeworks = response['homeworks']
    if isinstance(homeworks, Dict):
        raise exceptions.HomeworkTypeError('Под ключем homeworks не dict')
    return homeworks


def parse_status(homework):
    """Извлечение статуса."""
    if 'homework_name' not in homework or 'status' not in homework:
        raise KeyError('Отсутсвуют нужные ключи в homework')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise exceptions.HomeworkStatusError('Ошибка статуса')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка токенов."""
    return all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PRACTICUM_TOKEN])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Токены не достопны')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    previous_msg = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                if previous_msg != message:
                    send_message(bot, message)
                    previous_msg = message
            else:
                logger.debug(
                    f'Статус не изменился, повторный запрос через '
                    f'{RETRY_TIME} минут'
                )
            current_timestamp = int(time.time())
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if previous_msg != message:
                send_message(bot, message)
                previous_msg = message
        else:
            logger.debug('Повторный запрос')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
