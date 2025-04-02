# Sensitive Data Exposure Lab

Hey there! 👋 This is a standalone lab I built for "Sensitive Data Exposure" - one of the OWASP Top 10 security vulnerabilities. It's a hands-on way to learn about how data leaks happen and how to prevent them.

## What's This All About?

This lab demonstrates how sensitive information (like credit cards, SSNs, and API keys) can accidentally get exposed in web apps. I've deliberately built in several security flaws so you can practice finding them - it's like a security treasure hunt.

## Getting Started

### What You'll Need

- Docker and Docker Compose (that's it!)

### How to Run It

Just follow these steps:

1. Clone this repo
2. CD into the project folder
3. Fire up Docker:

```bash
docker-compose up -d
```

4. Open your browser and head to http://localhost:8000

### Quick Testing

Don't want to create an account? No worries! Use the demo login:
- Username: `demo`
- Password: `demopass`

### Ugh, It's Not Working!

If you hit database errors, try this:

```bash
# The nuclear option - rebuild everything
docker-compose down
docker-compose up --build

# Or just run the migrations
docker-compose exec web python manage.py makemigrations dataexposure
docker-compose exec web python manage.py migrate
```

## What You'll Learn

This lab will help you:
1. Spot different ways sensitive data gets leaked
2. Understand why proper data protection matters
3. Learn how hackers find and exploit these issues
4. Discover best practices for keeping sensitive data safe

## The Security Flaws

I've hidden several security problems for you to find (don't peek at this list until you've tried!):

1. Comments in HTML with sensitive data (check the page source!)
2. JavaScript that exposes API keys
3. Unprotected API endpoints anyone can access
4. Data stored in localStorage (check your browser)
5. Partial data masking that's easy to bypass
6. A public API that leaks EVERYONE'S data (yikes!)
7. Missing access controls that let you see other people's info

## Fair Warning ⚠️

This app is INTENTIONALLY INSECURE. Don't put any real personal info in it! And definitely don't deploy it to a public server unless you want to give hackers a practice playground.

---

Happy hacking (ethically, of course)