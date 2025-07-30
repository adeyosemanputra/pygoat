# Software and Data Integrity Failures Lab

This lab demonstrates common software and data integrity failures through two practical examples:

1. **Lab 1: Insecure Deserialization**
   - Demonstrates pickle deserialization vulnerabilities in Python
   - Learn about object injection attacks
   - Practice exploiting cookie-based authentication

2. **Lab 2: Software Supply Chain Attack**
   - Shows how download links can be manipulated
   - Demonstrates client-side injection vulnerabilities
   - Learn about supply chain integrity issues

## Running the Lab

1. Build and start the container:
   ```bash
   docker-compose up --build
   ```

2. Access the lab at http://localhost:5011

## Lab Solutions

### Lab 1 Solution
To solve Lab 1, you need to:
1. Get the cookie value and base64 decode it
2. Create a malicious pickle payload that sets admin=1
3. Base64 encode the payload and replace the cookie

### Lab 2 Solution
To solve Lab 2:
1. Input a username with XSS payload that modifies the download link
2. The download link can be changed to fetch fake.txt instead of real.txt

## Security Notes
This is a deliberately vulnerable application for educational purposes. Do not use any of these practices in production code.
