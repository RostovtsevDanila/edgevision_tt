"""Controller
    Компонент, который по TCP соединению управляет манипулятором, на базе данных от сенсоров.
Алгоритм принятия решения о статусе на усмотрение, но должен использовать данные с сенсоров.
    Обработка данных с сенсоров происходит параллельно/асинхронно, однако важно обрабатывать
сообщения в интервалы 5 секунд. Т. е. каждые 5 секунд принимается решение об управляющем
сигнале для манипулятора.
    Outdated информация не должна приниматься во внимание при принятии решения. Сообщение
считается outdated, если информация из этого сообщения была получена раньше принятия
последнего решения об управляющем сигнале.
"""


from aiohttp import web
from data_driver import DataDriver
import datetime
from os import environ
import socket
import json
import schedule
import time
import threading


MANIPULATOR_HOST = str(environ.get("MANIPULATOR_HOST"))
MANIPULATOR_PORT = int(environ.get("MANIPULATOR_PORT"))

CURRENT_DATA = DataDriver()
CURRENT_TIME_PERIOD: datetime


def send_signal():
    # Принятие решения
    data = dict({
        "datetime": datetime.datetime.now().strftime("%Y%m%dT%H%M%S"),
        "status": "up" if CURRENT_DATA.value > 0 else "down"
    })
    print(data, CURRENT_DATA.value)
    print(f"Data counter: {CURRENT_DATA.counter}")
    
    # С этого момента начинается набор новых данных. Старые данные не будут учитываться
    # при принятии следующего решения, т.к. среднее значение снова равно нулю
    CURRENT_DATA.obnulis()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as m_socket:
        m_socket.connect((MANIPULATOR_HOST, MANIPULATOR_PORT))
        encoded_data = json.dumps(data, indent=2).encode("utf-8")
        m_socket.send(encoded_data)
        m_socket.close()


def scheduler():
    schedule.every(5).seconds.do(send_signal)
    while True:
        schedule.run_pending()
        time.sleep(1 / 1000)


def compute_data(data: dict):
    CURRENT_DATA.add_data(data.get("payload"))


async def receive_msg(request):
    request = await request.json()
    compute_data(request)
    return web.json_response({"status": "Ok"})


app = web.Application()
app.add_routes([web.post('/msg', receive_msg)])

if __name__ == '__main__':
    threading.Thread(target=scheduler, args=()).start()
    web.run_app(app, host="0.0.0.0", port=9999)
