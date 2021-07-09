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


from flask import Flask, request, Response
from data_driver import DataDriver
import socket
import json
from datetime import datetime
import schedule
import time
import threading


app = Flask("Controller")


MANIPULATOR_HOST = "manipulator"
MANIPULATOR_PORT = 9997
current_data = DataDriver()


def send_signal():
    data = dict({
        "datetime": datetime.now().strftime("%Y%m%dT%H%M%S"),
        "status": "up" if current_data.current_data > 0 else "down"
    })
    print(data, current_data.current_data)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((MANIPULATOR_HOST, MANIPULATOR_PORT))
    encoded_data = json.dumps(data, indent=2).encode("utf-8")
    sock.send(encoded_data)
    sock.close()
    current_data.obnulis()


def scheduler():
    schedule.every(5).seconds.do(send_signal)
    while True:
        schedule.run_pending()
        time.sleep(1)


def compute_data(data: dict):
    current_data.add_data(data.get("payload"))


@app.route("/msg", methods=["POST"])
def receive_msg():
    if request.method == "POST":
        compute_data(data := request.json)
    return "Ok"


if __name__ == '__main__':
    threading.Thread(target=scheduler, args=()).start()
    app.run(host="0.0.0.0", port=9999)

