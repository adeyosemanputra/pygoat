# Challenge System — API Documentation

Endpoints exposed by `DoItFast` in `challenge/views.py`.

## Base URL
`/challenge/<challenge_name>`

## Authentication
All endpoints require an authenticated session.
PUT returns JSON `{"status": "401"}`. Others redirect to `/login`.

---

## GET `/challenge/<challenge_name>`
Renders the challenge page. No body required.

---

## POST `/challenge/<challenge_name>`
Starts a Docker container. Implements intelligent container reuse:
- `is_live=True` returns existing endpoint immediately (no Docker call)
- `is_live=False` attempts docker start, falls back to docker run if gone
- New user runs docker run directly

**Success:** `{"message": "success", "status": "200", "endpoint": "http://localhost:<port>"}`
**Already running:** `{"message": "already running", "status": "200", "endpoint": "..."}`
**Error:** `{"message": "failed", "status": "500", "endpoint": "None"}`

---

## DELETE `/challenge/<challenge_name>`
Stops the container and sets is_live=False.

**Success:** `{"message": "success", "status": "200"}`
**Error:** `{"message": "failed", "status": "500"}`

---

## PUT `/challenge/<challenge_name>`
Validates a flag submission. Request body: {"flag": "<plaintext_flag>"}

Hashes submitted flag as hashed_ + sha256(flag) server-side and compares to stored value.

Correct flag: {"message": "correct", "status": "200", "points": N}
Wrong flag: {"message": "incorrect", "status": "200"} — increments no_of_attempt
Empty flag: {"message": "no flag provided", "status": "400"}
Malformed JSON: {"message": "invalid request body", "status": "400"}
Unauthenticated: {"message": "unauthorized", "status": "401"}
Unknown challenge: {"message": "challenge not found", "status": "404"}

---

## Running Tests
python manage.py test challenge
