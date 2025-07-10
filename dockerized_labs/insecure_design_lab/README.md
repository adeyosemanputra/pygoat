# Insecure Design Lab

This is a standalone lab demonstrating the OWASP Top 10 2021 category A04: Insecure Design. The lab simulates a movie ticket booking system with an intentional design flaw that allows bypassing ticket limits.

## Vulnerability

The lab demonstrates insecure design through:
1. A per-user ticket limit that can be bypassed by creating multiple accounts
2. No proper user uniqueness validation
3. Predictable business logic for ticket validation

## Setup

1. Make sure you have Docker and Docker Compose installed
2. Clone the repository
3. Navigate to the lab directory
4. Run:
```bash
docker-compose up --build
```
5. Visit http://localhost:5008 in your browser

## Challenge

The goal is to exploit the insecure design to:
1. Get more than 5 tickets despite the per-user limit
2. Discover how the ticket validation system can be bypassed

## Solution

<details>
<summary>Click to reveal solution</summary>

1. Register multiple accounts to bypass the 5-ticket limit per user
2. Use each account to claim tickets
3. The system only checks total ticket count and ownership, allowing multiple users to circumvent the intended restrictions

A secure design would:
- Implement proper user identity verification
- Use unique constraints beyond just usernames
- Have better business logic validation
</details>
