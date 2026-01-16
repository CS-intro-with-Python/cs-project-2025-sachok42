from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dev-secret-key"
DB = "database.db"


def get_db():
    return sqlite3.connect(DB)


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS diagrams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            diagram_data TEXT NOT NULL,
            thumbnail TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        with get_db() as db:
            try:
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (request.form["username"],
                     generate_password_hash(request.form["password"]))
                )
                return redirect("/login")
            except sqlite3.IntegrityError:
                return "Username already exists", 400
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = get_db().execute(
            "SELECT id, password_hash FROM users WHERE username=?",
            (request.form["username"],)
        ).fetchone()

        if user and check_password_hash(user[1], request.form["password"]):
            session["user_id"] = user[0]
            return redirect("/")
        return "Invalid credentials", 401

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html")


@app.route("/save_diagram", methods=["POST"])
def save_diagram():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    with get_db() as db:
        db.execute(
            """INSERT INTO diagrams (user_id, name, diagram_data, thumbnail)
               VALUES (?, ?, ?, ?)""",
            (
                session["user_id"],
                data["name"],
                json.dumps(data["diagram"]),
                data.get("thumbnail", "")
            )
        )
    return jsonify({"status": "ok"})


@app.route("/load_thumbnails")
def load_thumbnails():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    rows = get_db().execute(
        "SELECT id, name, thumbnail, created_at FROM diagrams WHERE user_id=? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()

    return jsonify([
        {"id": r[0], "name": r[1], "thumbnail": r[2], "created_at": r[3]}
        for r in rows
    ])


@app.route("/load_diagram/<int:diagram_id>")
def load_diagram(diagram_id):
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    row = get_db().execute(
        "SELECT diagram_data FROM diagrams WHERE id=? AND user_id=?",
        (diagram_id, session["user_id"])
    ).fetchone()

    if not row:
        return jsonify({"error": "Diagram not found"}), 404

    return jsonify(json.loads(row[0]))


@app.route("/delete_diagram/<int:diagram_id>", methods=["DELETE"])
def delete_diagram(diagram_id):
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    with get_db() as db:
        db.execute(
            "DELETE FROM diagrams WHERE id=? AND user_id=?",
            (diagram_id, session["user_id"])
        )
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001, host="0.0.0.0")