from flask import Flask, request
import sqlite3
from pathlib import Path

app = Flask(__name__)

DB_PATH = Path(__file__).with_name("messages.db")


def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.route("/", methods=["POST"])
def receive_message():
    message = request.get_data(as_text=True)

    if not message.strip():
        return "Message cannot be empty!", 400

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO messages (message) VALUES (?)",
        (message,)
    )

    connection.commit()
    connection.close()

    return "Message successfully saved!", 201


if __name__ == "__main__":
    init_db()
    app.run(port=8000)