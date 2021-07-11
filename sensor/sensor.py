"""
Sensor
Компонент, генерирующий данные, на основе которых контроллер принимает решение.
Всего 8 сенсоров, каждый генерирует 300 сообщений в секунду, сообщения равномерно
распределены по секунде и отправляются раздельно
(один запрос на одно сообщение).
Алгоритм генерации данных на усмотрение.
"""


from datetime import datetime
from os import environ
import random
import time
import requests

CONTROLLER_HOST = str(environ.get("CONTROLLER_HOST"))
CONTROLLER_PORT = int(environ.get("CONTROLLER_PORT"))
MESSAGE_FREQUENCY = 1 / 300     # sec
COLLECTOR_MESSAGE_ENDPOINT = "/msg"


def generate_message() -> dict:
    return {
        "datetime": datetime.now().strftime("%Y%m%dT%H%M%S"),
        "payload": random.randint(-1024, 1024),
    }


def send_message(msg: dict):
    try:
        res = requests.post(
            f"http://{CONTROLLER_HOST}:{CONTROLLER_PORT}{COLLECTOR_MESSAGE_ENDPOINT}",
            json=msg,
        )
        return res

    except requests.exceptions.ConnectionError as err:
        return err


def main():
    while True:
        time.sleep(MESSAGE_FREQUENCY)
        msg = generate_message()
        print(send_message(msg))


if __name__ == '__main__':
    main()
