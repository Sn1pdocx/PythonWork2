import socket

class FileServer:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port

    def receive_file(self, conn, filename):
        with open(filename, "wb") as file:
            while True:
                data = conn.recv(4096)

                if not data:
                    break

                file.write(data)

    def handle_client(self, conn, filename):
        self.receive_file(conn, filename)

        print("Файл отриманий!")
        conn.sendall(
            "Файл отримано сервером".encode("utf-8")
        )

    def run(self, max_clients=None):
        with socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM) as server:
            server.bind((self.host, self.port))
            server.listen()

            print(f"Сервер запущено: {self.host}:{self.port}")

            count = 0

            while max_clients is None or count < max_clients:
                conn, addr = server.accept()

                with conn:
                    print(f"Підключився клієнт: {addr}")
                    self.handle_client(conn, "received.txt")

                count += 1

if __name__ == "__main__":
    server = FileServer()
    server.run()