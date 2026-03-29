# SQL Injection Lab

This lab demonstrates a SQL injection vulnerability in a simple login form. It is part of the PyGoat project and has been converted to a standalone Flask application.

## Running the Lab

1. Build and start the container:
   ```bash
   docker-compose up --build
   ```

2. Access the lab at http://localhost:5012

## Vulnerability Description

The lab contains a deliberately vulnerable login form that is susceptible to SQL injection attacks. The vulnerability exists because user input is directly concatenated into SQL queries without proper sanitization.

## Lab Solutions

The lab can be solved by:
1. Using `admin' OR '1'='1` as the password
2. Alternatively, you can use any variant of SQL injection that makes the WHERE clause always true

## Security Notes
This is a deliberately vulnerable application for educational purposes. Do not use any of these practices in production code.
