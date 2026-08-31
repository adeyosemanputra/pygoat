# A09 – Silent Privilege Escalation (Security Logging & Alerting Failures)

## Overview

This lab demonstrates a class of security failure where high-risk actions
are correctly logged but fail to trigger alerts under certain conditions.
The application appears to have logging and alerting in place, yet a
privilege escalation can occur silently.

The goal of this lab is to highlight how security monitoring can be bypassed
when trust decisions are inferred from client-controlled context rather than
enforced server-side.

This lab aligns with **OWASP Top 10:2025 – A09: Security Logging and Alerting Failures**.

---

## Learning Objectives

By completing this lab, you will learn how:

- Logging alone does not guarantee detection
- Alert logic can be conditionally bypassed
- Privilege escalation can succeed silently
- Secure design enforces authorization independently of client input
- Detection should be based on intent, not just failure

---

## Lab Structure

The lab provides two operating modes:

- **Vulnerable Mode**
  - Logging exists
  - Alerts are conditionally triggered
  - Privilege escalation may succeed silently

- **Secure Mode**
  - Authorization is enforced server-side
  - Client-supplied context is ignored
  - Privilege escalation attempts trigger alerts

A toggle is available in the dashboard to switch between modes.

---

## Getting Started

### Starting the Lab

From the lab directory, start the application using Docker Compose:
```
docker compose up --build
```

The application will start in the foreground.

---

### Accessing the Lab

How you access the lab depends on how it was launched:

- **If only the Silent Privilege Escalation lab is running**
  
  Access it directly at:
  
```
http://172.19.0.2:5000
```

- **If the full A09 lab set is launched via Docker Compose**

Access the Silent Privilege Escalation lab at:
```
http://localhost:5109/
```

---

### Stopping the Lab

To stop the lab and shut down containers, press:

```
Ctrl + C
```

---

## Success Criteria

The lab is considered complete when:

- A non-admin user is able to obtain administrative privileges
- No security alert is triggered during that escalation
- Logs still record the action

You should then switch to **Secure Mode** and confirm that the same behavior
is no longer possible.

---

## Notes

- This lab is designed to encourage experimentation.
- Try repeating the same actions in both Vulnerable and Secure modes.
- Focus on how the system decides when to alert, not just whether it logs.
- Use separate browsers or private windows to test multiple users simultaneously

---

## Solution & Walkthrough

A detailed walkthrough explaining the intended reasoning process,
exploit logic, and secure fix is available in the solution documentation
for this lab.

Please review it **only after completing the exercise**.

