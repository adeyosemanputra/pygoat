from dataclasses import dataclass
import base64
import binascii
import json

from flask import Flask, make_response, render_template, request

app = Flask(__name__)

MAX_USERNAME_LENGTH = 100


@dataclass
class User:
    username: str
    is_admin: bool = False


def valid_username(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    username = value.strip()
    if not username or len(username) > MAX_USERNAME_LENGTH:
        return None

    return username


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/serialize", methods=["POST"])
def serialize_data():
    username = valid_username(request.form.get("username", ""))

    if username is None:
        return render_template(
            "result.html",
            message="Invalid username.",
        ), 400

    # JSON is data only; it cannot reconstruct arbitrary Python objects.
    payload = {"username": username}
    serialized = base64.b64encode(
        json.dumps(payload).encode("utf-8")
    ).decode("ascii")

    return render_template("result.html", serialized=serialized)


@app.route("/deserialize", methods=["POST"])
def deserialize_data():
    serialized_data = request.form.get("serialized_data", "")

    try:
        decoded_data = base64.b64decode(serialized_data, validate=True)
        payload = json.loads(decoded_data.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
        return render_template(
            "result.html",
            message="Invalid user data.",
        ), 400

    # Accept exactly one unprivileged client field.
    if not isinstance(payload, dict) or set(payload) != {"username"}:
        return render_template(
            "result.html",
            message="Invalid user data.",
        ), 400

    username = valid_username(payload.get("username"))

    if username is None:
        return render_template(
            "result.html",
            message="Invalid user data.",
        ), 400

    # Never take is_admin from client input.
    # In a real application, look up privileges from trusted server-side storage.
    user = User(username=username, is_admin=False)

    if user.is_admin:
        message = f"Welcome Admin {user.username}!"
    else:
        message = f"Welcome {user.username}. Only admins can see the secret content."

    return render_template("result.html", message=message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
