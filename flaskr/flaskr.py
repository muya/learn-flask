# all the imports
import sqlite3

import logging
from logging import FileHandler
from logging import Formatter as LogFormatter

from flask import (Flask, request, session, g, redirect, url_for, abort,
                   render_template, flash)
from contextlib import closing

# config in flaskrconfig.py file

# create application
app = Flask(__name__)
# from_object will look at the given object (if it is a string it will import
# it) and then look for all uppercase variables defined there.
app.config.from_object(__name__)
app.config.from_envvar("FLASKR_SETTINGS", silent=True)


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()


# db functions
def connect_db():
    return sqlite3.connect(app.config["DATABASE"])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


# view functions
@app.route("/")
def show_entries():
    cur = g.db.execute("SELECT title, content FROM entries ORDER BY id DESC")
    entries = [dict(title=row[0], content=row[1]) for row in cur.fetchall()]
    return render_template("show_entries.html", entries=entries)


@app.route("/add", methods=["POST"])
def add_entry():
    if not session.get("logged_in"):
        abort(401)

    g.db.execute(
        "INSERT INTO entries (title, content) VALUES (?, ?)",
        [request.form["title"], request.form["content"]])
    g.db.commit()
    flash("New entry added!")
    return redirect(url_for("show_entries"))


# log in and logout
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    app.logger.error("login called")

    if request.method == "POST":
        if request.form["username"] != app.config["USERNAME"]:
            error = "Invalid username"
        elif request.form["password"] != app.config["PASSWORD"]:
            error = "Invalid password"
        else:
            session["logged_in"] = True
            flash("Logged in!")
            return redirect(url_for("show_entries"))

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("Logged out!")
    return redirect(url_for("show_entries"))

# config logging
file_handler = FileHandler(app.config["LOG_FILE"])
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(LogFormatter(
    "%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d"))
app.logger.addHandler(file_handler)

if __name__ == "__main__":
    app.run(host=app.config["SERVER_HOST"])
