# Broken Authentication Lab

This is a deliberately vulnerable web application that demonstrates common authentication vulnerabilities. It is designed for educational purposes to help understand various authentication security issues and their prevention.

## Vulnerabilities Included

1. Weak Password Requirements
2. Plain Text Password Storage
3. Insecure Session Management
4. Vulnerable "Remember Me" Functionality
5. Predictable Password Reset Tokens
6. No Brute Force Protection
7. Debug Mode Enabled in Production

## Setup Instructions

### Prerequisites
- Docker
- Docker Compose

### Running the Lab

1. Clone the repository
2. Navigate to the broken_auth_lab directory
3. Build and run the container:
   ```bash
   docker-compose up --build
   ```
4. Access the lab at http://localhost:5000

### Default Credentials

The lab comes with two pre-configured users:
- Admin User:
  - Username: admin
  - Password: admin123
  - Email: admin@example.com

- Regular User:
  - Username: user
  - Password: password123
  - Email: user@example.com

## Lab Exercises

1. **Password Policy Bypass**
   - Try to create accounts with weak passwords
   - Observe the lack of password requirements

2. **Session Token Analysis**
   - Login with remember me enabled
   - Analyze the session cookie structure
   - Try to manipulate the session token

3. **Password Reset Exploitation**
   - Request a password reset
   - Analyze the reset token generation
   - Try to predict or manipulate reset tokens

4. **Role Escalation**
   - Login as a regular user
   - Try to escalate privileges to admin

## Security Notice

This application contains intentional security vulnerabilities for educational purposes. DO NOT deploy this in a production environment or expose it to the public internet.

## Prevention Tips

1. Implement strong password policies
2. Use secure password hashing (bcrypt, Argon2)
3. Implement proper session management
4. Use secure token generation
5. Implement rate limiting and brute force protection
6. Use HTTPS
7. Implement proper access controls
8. Enable security headers
9. Use secure configuration in production 