# BOPLA Lab - Broken Object Property Level Authorization

## Overview

This lab demonstrates **Broken Object Property Level Authorization (BOPLA)**, a critical security vulnerability where APIs return sensitive object properties that users should not have access to, even if the frontend doesn't display them.

## Vulnerability Description

BOPLA occurs when:
- APIs return complete object data regardless of user permissions
- Frontend applications filter sensitive data but APIs don't
- Authorization is implemented only at the UI level, not at the API level
- Different user roles should see different object properties but receive the same data

## Lab Setup

### Running the Lab

1. Navigate to the lab directory:
```bash
cd challenge/bopla_lab/
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask application:
```bash
python app.py
```

4. Access the lab at: `http://localhost:8080`

### Test Credentials

- **Developer**: user1 / password123
- **Manager**: user2 / pass456  
- **Admin**: admin / admin123

## Learning Objectives

1. Understand what BOPLA vulnerability is
2. Learn to identify over-exposed API endpoints
3. Practice API security testing techniques
4. Understand proper property-level authorization
5. Learn the difference between frontend filtering and backend security

## Exploitation Steps

1. **Login** with any test account
2. **Access the dashboard** and view projects
3. **Open browser developer tools** (F12 → Network tab)
4. **Click on projects** and observe API calls
5. **Analyze API responses** for sensitive data
6. **Compare** what frontend shows vs what API returns
7. **Test with different user roles** to see if responses differ

## Expected Findings

The vulnerable endpoint `/api/project/{id}/details` returns sensitive data including:
- Budget information
- Client credentials  
- Internal notes
- Team member emails

Even though the frontend only displays project name and description, this sensitive data is accessible through:
- Browser developer tools
- Direct API calls
- Proxy tools like Burp Suite

## Mitigation

The lab also includes a secure endpoint `/api/project/{id}/safe` that demonstrates proper property-level authorization:
- Returns different data based on user role
- Filters out sensitive information appropriately
- Never exposes highly sensitive data like credentials

## Tools for Testing

- Browser Developer Tools
- Burp Suite or OWASP ZAP
- Postman or curl
- Network analysis tools

## OWASP API Security Top 10

This vulnerability relates to:
- **API3:2023 - Broken Object Property Level Authorization**
- Demonstrates importance of server-side data filtering
- Shows risks of relying on client-side security controls