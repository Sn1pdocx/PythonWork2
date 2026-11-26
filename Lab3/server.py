from flask import Flask, request, jsonify
from functools import wraps
from werkzeug.security import check_password_hash
from database import get_db_connection, init_db
app = Flask(__name__)

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization

        if auth and auth.type == "basic" and auth.username and auth.password:
            conn = get_db_connection()

            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (auth.username,)
            ).fetchone()

            conn.close()

            if user and check_password_hash(
                user["password_hash"], auth.password
            ):
                return func(*args, **kwargs)

        return jsonify({
            "error": "Invalid username or password"
        }), 401, {"WWW-Authenticate": 'Basic realm="GuitarHub"'}

    return wrapper

@app.route("/items", methods=["GET"])
@require_auth
def get_items():
    brand = request.args.get("brand")

    conn = get_db_connection()

    if brand:
        items = conn.execute(
            "SELECT * FROM items WHERE brand LIKE ?",
            (f"%{brand}%",)
        ).fetchall()
    else:
        items = conn.execute(
            "SELECT * FROM items"
        ).fetchall()

    conn.close()

    return jsonify([dict(item) for item in items]), 200

@app.route("/items/<int:item_id>", methods=["GET"])
@require_auth
def get_item(item_id):
    conn = get_db_connection()

    item = conn.execute(
        "SELECT * FROM items WHERE id = ?",
        (item_id,)
    ).fetchone()

    conn.close()

    if item is None:
        return jsonify({"error": "Guitar not found"}), 404

    return jsonify(dict(item)), 200

def validate_item(data):
    if not isinstance(data, dict):
        return "Invalid JSON data"

    text_fields = ["brand", "model", "type", "color"]
    number_fields = ["strings", "price", "stock"]

    for field in text_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return f"Invalid or missing field: {field}"

    for field in number_fields:
        if type(data.get(field)) is not int:
            return f"Invalid or missing field: {field}"

    if data["strings"] <= 0:
        return "Number of strings must be positive"

    if data["price"] < 0:
        return "Price cannot be negative"

    if data["stock"] < 0:
        return "Stock cannot be negative"

    return None

@app.route("/items", methods=["POST"])
@require_auth
def add_item():
    data = request.get_json(silent=True)

    error = validate_item(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    cursor = conn.execute("""
        INSERT INTO items
        (brand, model, type, strings, color, price, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["brand"],
        data["model"],
        data["type"],
        data["strings"],
        data["color"],
        data["price"],
        data["stock"]
    ))

    item_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Guitar added successfully",
        "id": item_id
    }), 201

@app.route("/items", methods=["PUT"])
@app.route("/items/<int:item_id>", methods=["PUT"])
@require_auth
def update_item(item_id=None):
    data = request.get_json(silent=True)

    error = validate_item(data)

    if error:
        return jsonify({"error": error}), 400

    if item_id is None:
        item_id = data.get("id")

    if type(item_id) is not int or item_id <= 0:
        return jsonify({"error": "Invalid guitar ID"}), 400

    conn = get_db_connection()

    cursor = conn.execute("""
        UPDATE items
        SET brand = ?, model = ?, type = ?,
            strings = ?, color = ?, price = ?, stock = ?
        WHERE id = ?
    """, (
        data["brand"],
        data["model"],
        data["type"],
        data["strings"],
        data["color"],
        data["price"],
        data["stock"],
        item_id
    ))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Guitar not found"}), 404

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Guitar updated successfully",
        "id": item_id
    }), 200

@app.route("/items", methods=["DELETE"])
@app.route("/items/<int:item_id>", methods=["DELETE"])
@require_auth
def delete_item(item_id=None):
    if item_id is None:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON data"}), 400

        item_id = data.get("id")

    if type(item_id) is not int or item_id <= 0:
        return jsonify({"error": "Invalid guitar ID"}), 400

    conn = get_db_connection()

    cursor = conn.execute(
        "DELETE FROM items WHERE id = ?",
        (item_id,)
    )

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Guitar not found"}), 404

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Guitar deleted successfully",
        "id": item_id
    }), 200

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000)
