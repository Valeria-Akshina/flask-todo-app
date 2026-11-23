import os
import sqlite3
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo.sqlite")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()


@app.route("/", methods=["GET"])
def index():
    with get_db() as conn:
        tasks = conn.execute("SELECT id, title, done FROM tasks ORDER BY id DESC").fetchall()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    if title:
        with get_db() as conn:
            conn.execute("INSERT INTO tasks (title, done) VALUES (?, 0)", (title,))
            conn.commit()
    return redirect(url_for("index"))


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    with get_db() as conn:
        conn.execute(
            "UPDATE tasks SET done = CASE WHEN done = 0 THEN 1 ELSE 0 END WHERE id = ?",
            (task_id,),
        )
        conn.commit()
    return redirect(url_for("index"))



@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    with get_db() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 7345))
    app.run(host="0.0.0.0", port=port)