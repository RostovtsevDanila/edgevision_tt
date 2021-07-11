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


from flask import Flask, request
from data_driver import DataDriver
from datetime import datetime
from os import environ
import socket
import json
import schedule
import time
import threading


app = Flask("Controller")

MANIPULATOR_HOST = str(environ.get("MANIPULATOR_HOST"))
MANIPULATOR_PORT = int(environ.get("MANIPULATOR_PORT"))

current_data = DataDriver()


def send_signal():
    data = dict({
        "datetime": datetime.now().strftime("%Y%m%dT%H%M%S"),
        "status": "up" if current_data.value > 0 else "down"
    })
    print(data, current_data.value)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as m_socket:
        m_socket.connect((MANIPULATOR_HOST, MANIPULATOR_PORT))
        encoded_data = json.dumps(data, indent=2).encode("utf-8")
        m_socket.send(encoded_data)
        m_socket.close()
    current_data.obnulis()


def scheduler():
    schedule.every(5).seconds.do(send_signal)
    while True:
        schedule.run_pending()
        time.sleep(1 / 300)


def compute_data(data: dict):
    current_data.add_data(data.get("payload"))


@app.route("/msg", methods=["POST"])
def receive_msg():
    if request.method == "POST":
        compute_data(request.json)
        return {"status": "Ok"}
    return {"status": "Fail"}


if __name__ == '__main__':
    threading.Thread(target=scheduler, args=()).start()
    app.run(host="0.0.0.0", port=9999)

