# Blind SQL Injection Lab

This lab demonstrates a **Blind SQL Injection** vulnerability using a login workflow.
It is intentionally vulnerable and built for security learning.

## What is Blind SQL Injection?

Blind SQL injection happens when an application does not show raw SQL/database errors,
but still gives different responses for true vs false SQL conditions.

Attackers use these subtle differences to extract sensitive values one character at a time.

## Why this happens

- User input is concatenated directly into SQL queries
- SQL errors are hidden from users (so it looks "safe")
- Response behavior still leaks useful clues
- Error handling/logging are not designed for secure authentication flow

## Running the Lab

0. (Optional) Set the admin password via environment variable:

	```bash
	export BLIND_SQL_ADMIN_PASSWORD="YourAlphaNumPass"
	```

   If this variable is not provided, the lab generates an alphanumeric admin password
   on first initialization and prints it in container logs.

1. Build and run the container:

	```bash
	docker-compose up --build
	```

2. Open the lab:

	```
	http://localhost:5023
	```

## Lab Objective

- Open the challenge login page
- Use username: `admin`
- Discover the admin password through blind SQL behavior
- Intercept requests with Burp Suite and brute-force conditions step-by-step

When your injected condition is true, the application gives a hint message:

> You are going right. Keep testing one character at a time.

## Prevention Tips

- Use prepared statements / parameterized queries
- Never concatenate user input into SQL strings
- Return generic authentication responses
- Add brute-force protections (rate-limits, lockouts)
- Keep detailed error logs server-side only

## Security Notice

This project is intentionally vulnerable for educational use.
Do not deploy this code in production.