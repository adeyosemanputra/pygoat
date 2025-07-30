# Insufficient Logging & Monitoring Lab

This lab demonstrates the security risks associated with insufficient logging and monitoring in web applications. It includes two scenarios that highlight common logging vulnerabilities.

## Getting Started

1. Build and run the lab using Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Access the lab at `http://localhost:5014`

## Lab Scenarios

### Lab 1: Insufficient Login Attempt Logging
- Demonstrates poor logging of authentication attempts
- Allows brute force attacks without detection
- No rate limiting or account lockout
- Credentials for testing: username="admin", password="secretpass123"

### Lab 2: Missing Critical Event Logging
- Demonstrates lack of logging for critical security events
- Password changes not logged
- Role modifications not tracked
- No audit trail for security-relevant changes

## Learning Objectives

1. Understand the importance of proper logging and monitoring
2. Learn to identify insufficient logging practices
3. Understand how poor logging affects security incident detection
4. Learn best practices for implementing secure logging

## Security Best Practices

To implement proper logging and monitoring:

1. Authentication Events:
   - Log all authentication attempts (success and failure)
   - Include relevant context (timestamp, IP, user agent)
   - Implement rate limiting and account lockout

2. Critical Security Events:
   - Log all sensitive operations
   - Include user identity and action details
   - Maintain secure audit trails

3. Log Management:
   - Use secure logging mechanisms
   - Protect log integrity
   - Implement proper log rotation
   - Set up alerts for suspicious activity

## References

- [OWASP Top 10 2021 - A09 Security Logging and Monitoring Failures](https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [OWASP Security Logging Project](https://owasp.org/www-project-security-logging/)
