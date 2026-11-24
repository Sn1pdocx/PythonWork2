import socket

HOST = "127.0.0.1"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()

    print(f"Сервер запущено: {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()

        with conn:
            print(f"Підключився клієнт: {addr}")

            with open("received.txt", "wb") as file:
                while True:
                    data = conn.recv(4096)

                    if not data:
                        break

                    file.write(data)

            print("Файл отриманий!")
            conn.sendall("Файл отримано сервером".encode("utf-8"))