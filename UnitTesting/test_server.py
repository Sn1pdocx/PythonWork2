from unittest.mock import MagicMock, patch
from server import FileServer


def test_default_settings():
    server = FileServer()

    assert server.host == "127.0.0.1"
    assert server.port == 5000


def test_custom_settings():
    server = FileServer("192.168.1.1", 8080)

    assert server.host == "192.168.1.1"
    assert server.port == 8080


def test_receive_file(tmp_path):
    server = FileServer()
    conn = MagicMock()
    conn.recv.side_effect = [b"Hello ", b"bybizyan!", b""]

    filename = tmp_path / "received.txt"

    server.receive_file(conn, filename)

    assert filename.read_bytes() == b"Hello bybizyan!"


def test_receive_empty_file(tmp_path):
    server = FileServer()
    conn = MagicMock()
    conn.recv.return_value = b""

    filename = tmp_path / "empty.txt"

    server.receive_file(conn, filename)

    assert filename.exists()
    assert filename.read_bytes() == b""


def test_handle_client_file(tmp_path):
    server = FileServer()
    conn = MagicMock()
    conn.recv.side_effect = [b"Test message", b""]

    filename = tmp_path / "received.txt"

    server.handle_client(conn, filename)

    assert filename.read_bytes() == b"Test message"


def test_handle_client_response(tmp_path):
    server = FileServer()
    conn = MagicMock()
    conn.recv.side_effect = [b"Hello", b""]

    filename = tmp_path / "received.txt"

    server.handle_client(conn, filename)

    conn.sendall.assert_called_once_with(
        "Файл отримано сервером".encode("utf-8")
    )


def test_run_one_client():
    server = FileServer()
    conn = MagicMock()

    with patch("server.socket.socket") as mock_socket:
        sock = mock_socket.return_value.__enter__.return_value
        sock.accept.return_value = (conn, ("127.0.0.1", 12345))

        with patch.object(server, "handle_client") as handler:
            server.run(max_clients=1)

            sock.bind.assert_called_once_with(("127.0.0.1", 5000))
            sock.listen.assert_called_once()
            sock.accept.assert_called_once()
            handler.assert_called_once_with(conn, "received.txt")


def test_run_two_clients():
    server = FileServer()
    conn1 = MagicMock()
    conn2 = MagicMock()

    with patch("server.socket.socket") as mock_socket:
        sock = mock_socket.return_value.__enter__.return_value

        sock.accept.side_effect = [
            (conn1, ("127.0.0.1", 12345)),
            (conn2, ("127.0.0.1", 12346))
        ]

        with patch.object(server, "handle_client") as handler:
            server.run(max_clients=2)

            assert sock.accept.call_count == 2
            assert handler.call_count == 2