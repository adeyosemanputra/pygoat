from flask import Flask, render_template, request
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.config["SECRET_KEY"] = "blind-sql-lab-secret"


def init_db():
	db_path = Path("./database.db")
	if db_path.exists():
		return

	conn = sqlite3.connect("database.db")
	cursor = conn.cursor()

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS users (
			username TEXT PRIMARY KEY,
			password TEXT NOT NULL
		)
		"""
	)

	cursor.execute(
		"INSERT OR REPLACE INTO users (username, password) VALUES (?, ?)",
		("admin", "A9b7X2kQ"),
	)

	conn.commit()
	conn.close()


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/lab", methods=["GET", "POST"])
def lab():
	if request.method == "POST":
		username = request.form.get("username", "")
		password = request.form.get("password", "")

		sql_query = (
			f"SELECT username, password FROM users WHERE username='{username}' "
			f"AND password='{password}'"
		)

		try:
			conn = sqlite3.connect("database.db")
			cursor = conn.cursor()
			result = cursor.execute(sql_query).fetchone()
			conn.close()

			if username == "admin" and password == "A9b7X2kQ":
				return render_template(
					"lab.html",
					success="Welcome admin! You solved the blind SQL challenge.",
				)

			if result:
				return render_template(
					"lab.html",
					progress=(
						"You are going right. Keep testing one character at a time."
					),
				)

			return render_template(
				"lab.html",
				error="Invalid username or password",
			)
		except sqlite3.Error:
			return render_template(
				"lab.html",
				error="Invalid username or password",
			)

	return render_template("lab.html")


if __name__ == "__main__":
	init_db()
	app.run(host="0.0.0.0", port=5023, debug=True)