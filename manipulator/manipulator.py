import socket
import json
from os import environ

MANIPULATOR_HOST = str(environ.get("MANIPULATOR_HOST"))
MANIPULATOR_PORT = int(environ.get("MANIPULATOR_PORT"))


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as m_socket:
        m_socket.bind((MANIPULATOR_HOST, MANIPULATOR_PORT))
        m_socket.listen()
        while True:
            conn, address = m_socket.accept()
            print(f"Connected: {address}")
            while True:
                data = conn.recv(128)
                if not data:
                    break
                data = json.loads(data)
                print(data)
            conn.close()


if __name__ == '__main__':
    main()
