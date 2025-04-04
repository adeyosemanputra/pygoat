# 🧠 Insecure Design Lab (OWASP A04)

Hey there! 👋 This is a standalone lab for one of the most sneaky web issues — **Insecure Design**. It's all about how flawed logic (not just bad code) can lead to real vulnerabilities.

---

## 🚀 What’s This All About?

This lab simulates a basic movie ticket app that gives away **5 free tickets** per user.

But here's the catch: the app doesn’t really check who the user is. 😬 So you can:
- Log out
- Use a new name
- Claim more tickets...

Repeat as much as you want. Infinite freebies! 🎟️🎟️🎟️

This is a classic case of insecure design — the system works as intended... but it was designed *wrong*.

---

## 🛠️ How to Run It (with Docker)

All you need is Docker installed:

```bash
docker build -t insecure-design-lab .
docker run -p 5000:5000 insecure-design-lab
Now open your browser and head to: 👉 http://localhost:5000/login

🧪 What You’ll Learn
Why logic flaws are just as dangerous as code bugs

How insecure design happens even when "everything works"

Why trusting user input (like usernames) is never a good idea

How to fix bad design by thinking in terms of security-first

🎯 Try It Yourself
Log in as any name (no password required)

Claim your 5 free tickets

Log out, change the name, and do it again

Use a ticket to “watch” a movie

Think: how would you fix this?

⚠️ Heads Up
This app is deliberately vulnerable — don’t use real personal info. It’s meant for learning and local use only.

Think beyond bugs — design matters too. 🚧
