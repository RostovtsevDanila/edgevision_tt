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
import requests
from ratelimit import limits, sleep_and_retry


CONTROLLER_HOST = str(environ.get("CONTROLLER_HOST"))
CONTROLLER_PORT = int(environ.get("CONTROLLER_PORT"))
MESSAGE_FREQUENCY = 1 / 300     # sec
COLLECTOR_MESSAGE_ENDPOINT = "/msg"


def generate_data() -> dict:
    return {
        "datetime": datetime.now().strftime("%Y%m%dT%H%M%S"),
        "payload": random.randint(-1024, 1024),
    }


@sleep_and_retry
@limits(calls=1, period=MESSAGE_FREQUENCY)
def send_message(session: requests.Session, url: str, data: dict):
    res = session.post(url, json=data)
    print(res)


def start_job():
    with requests.Session() as session:
        adapter = requests.sessions.HTTPAdapter(
            pool_connections=300,
            pool_maxsize=300,
        )
        session.mount("http://", adapter)
        while True:
            send_message(
                session,
                url=f"http://{CONTROLLER_HOST}:{CONTROLLER_PORT}{COLLECTOR_MESSAGE_ENDPOINT}",
                data=generate_data(),
            )


def main():
    start_job()


if __name__ == '__main__':
    main()
