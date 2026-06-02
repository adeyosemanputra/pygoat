import jwt

SECRET = "pygoat-secret"


def create_session(user):
    payload = {"username": user, "is_staff": False}
    return jwt.encode(payload, SECRET, algorithm="none")


def read_session(token):
    return jwt.decode(token, SECRET, algorithms=["HS256", "none"])


if __name__ == "__main__":
    t = create_session("charlie")
    print(read_session(t))
