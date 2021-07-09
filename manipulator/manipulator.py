import socket
import json

MANIPULATOR_HOST = "manipulator"
MANIPULATOR_PORT = 9997


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as m_socket:
        m_socket.bind((MANIPULATOR_HOST, MANIPULATOR_PORT))
        m_socket.listen()
        while True:
            conn, address = m_socket.accept()
            print(f"Connected: {address}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = json.loads(data)
                print(data)
                # todo вывести в логфайл
                # conn.send("Ok".encode("utf-8").upper())
            conn.close()


if __name__ == '__main__':
    main()
