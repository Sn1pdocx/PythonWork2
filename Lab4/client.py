import socket

HOST = "127.0.0.1"
PORT = 5000

filename = input("Введіть назву текстового файлу: ")

with open(filename, "rb") as file:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))

        while True:
            data = file.read(4096)

            if not data:
                break

            client.sendall(data)

        client.shutdown(socket.SHUT_WR)

        response = client.recv(4096)
        print(response.decode("utf-8"))