# Security Headers Misconfiguration - Clickjacking Lab

## Overview

This lab demonstrates a critical security misconfiguration where a banking web application lacks proper security headers, making it vulnerable to clickjacking attacks. Attackers can embed the banking interface in malicious iframes to trick users into performing unintended actions.

## Vulnerability Details

- **Vulnerability Type**: Security Headers Misconfiguration - Clickjacking
- **Severity**: High
- **OWASP Category**: A05:2021 - Security Misconfiguration
- **CWE**: CWE-1021 (Improper Restriction of Rendered UI Layers)

## Lab Scenario

You're testing SecureBank's online banking application that processes money transfers. The application fails to implement proper security headers, allowing it to be embedded in malicious iframes. Attackers can create fake gaming or promotional sites that trick users into clicking hidden banking controls.

### Story
- **Setting**: SecureBank Online Banking System
- **Functionality**: Money transfer between accounts
- **Missing Security**: No X-Frame-Options or CSP frame-ancestors headers
- **Attack Vector**: Malicious iframe embedding with UI redressing

## Exploitation

### Step-by-Step Attack

1. **Access Banking System**
   - Navigate to `/login`
   - Use demo credentials to log in
   - Access the money transfer page

2. **Identify Missing Headers**
   - Check HTTP response headers
   - Verify absence of X-Frame-Options
   - Confirm missing CSP frame-ancestors directive

3. **Create Malicious Page**
   - Design attractive fake interface
   - Embed banking transfer page in hidden iframe
   - Position fake buttons over real banking controls

4. **Execute Clickjacking Attack**
   - Visit the malicious demonstration page (`/malicious`)
   - Observe how the banking page loads in iframe
   - See how user clicks could trigger hidden actions

### Demo Accounts
```
Username: john_doe
Password: password123
Balance: ₹25,000

Username: jane_smith  
Password: securepass
Balance: ₹15,000
```

### Malicious Page Structure
```html
<!-- Attractive fake interface -->
<div style="position: relative;">
    <button style="z-index: 1;">🎮 PLAY NOW - WIN PRIZES! 🏆</button>
    
    <!-- Hidden banking iframe -->
    <iframe src="/transfer" 
            style="position: absolute; opacity: 0.01; z-index: 10;">
    </iframe>
</div>
```

## Vulnerable Code Analysis

### The Problem
```python
# VULNERABLE: Missing security headers
@app.after_request
def after_request(response):
    # No X-Frame-Options header
    # No Content-Security-Policy frame-ancestors
    # Allows iframe embedding from any origin
    return response
```

### What Makes It Vulnerable
1. **No Frame Protection**: Missing X-Frame-Options header
2. **No CSP**: Missing Content-Security-Policy frame-ancestors directive
3. **Implicit Allow**: Default browser behavior allows iframe embedding
4. **Session Hijacking**: User sessions remain valid in iframes

## Secure Implementation

### Fixed Code
```python
def add_security_headers(response, secure_mode=False):
    if secure_mode:
        # SECURE: Prevent iframe embedding
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'none'"
        
        # Additional security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response
```

### Security Headers Explained

1. **X-Frame-Options (Legacy)**
```http
X-Frame-Options: DENY                    # Block all iframe embedding
X-Frame-Options: SAMEORIGIN             # Allow same-origin only
X-Frame-Options: ALLOW-FROM https://...  # Allow specific domain
```

2. **Content-Security-Policy (Modern)**
```http
Content-Security-Policy: frame-ancestors 'none'          # Block all
Content-Security-Policy: frame-ancestors 'self'         # Same-origin only  
Content-Security-Policy: frame-ancestors 'self' https://trusted.com
```

3. **Additional Security Headers**
```http
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Lab Features

### Interactive Security Testing
- **Vulnerable Mode**: Demonstrates missing security headers
- **Secure Mode**: Shows proper header implementation
- **Live Header Inspection**: Real-time header checking
- **Iframe Embedding Test**: Visual demonstration of clickjacking

### Educational Components
- **Banking Simulation**: Realistic money transfer interface
- **Malicious Page Demo**: Practical clickjacking demonstration
- **Security Toggle**: Compare vulnerable vs secure configurations
- **Browser Testing**: Cross-browser compatibility testing

## Testing Instructions

### Manual Testing
1. **Start the Lab**:
   ```bash
   cd /home/garvita/docker_apps/pygoat/dockerized_labs/security_headers_lab
   docker-compose up
   ```

2. **Access the Application**: Navigate to `http://localhost:5011`

3. **Test Vulnerable Mode**:
   - Ensure secure mode is disabled
   - Login to banking system
   - Check response headers: `curl -I http://localhost:5011/transfer`
   - Visit malicious page and observe iframe loading

4. **Test Secure Mode**:
   - Enable secure mode
   - Check updated headers
   - Verify iframe blocking in malicious page

### Automated Testing
```bash
# Test vulnerable mode
curl -I http://localhost:5011/transfer
# Should NOT see X-Frame-Options or CSP headers

# Test secure mode (after enabling)
curl -I http://localhost:5011/transfer
# Should see: X-Frame-Options: DENY
# Should see: Content-Security-Policy: frame-ancestors 'none'
```

### Browser Testing
```javascript
// Test iframe embedding
const iframe = document.createElement('iframe');
iframe.src = 'http://localhost:5011/transfer';
document.body.appendChild(iframe);

// Check console for blocking messages:
// "Refused to display ... in a frame because it set 'X-Frame-Options' to 'deny'"
```

## Real-World Attack Scenarios

### Banking Fraud
```html
<!-- Fake promotional page -->
<h1>🎁 Win $1000 - Click to Claim Your Prize!</h1>
<div style="position: relative;">
    <button id="fake-button">CLAIM PRIZE NOW!</button>
    <iframe src="https://bank.com/transfer" 
            style="position: absolute; opacity: 0.01; z-index: 2;"></iframe>
</div>
```

### Social Media Manipulation
```html
<!-- Hidden social media actions -->
<button>Play Free Game</button>
<iframe src="https://social.com/follow/attacker" style="opacity: 0;"></iframe>
```

### Browser Extension Installation
```html
<!-- Tricked extension installation -->
<button>Continue to Video</button>
<iframe src="chrome://extensions/install/malicious-ext" style="opacity: 0;"></iframe>
```

## Prevention & Mitigation

### Implementation Guide

#### Flask Implementation
```python
from flask import Flask

@app.after_request
def security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'none'"
    return response
```

#### Apache Configuration
```apache
# In .htaccess or virtual host
Header always set X-Frame-Options "DENY"
Header always set Content-Security-Policy "frame-ancestors 'none'"
```

#### Nginx Configuration
```nginx
# In server block
add_header X-Frame-Options "DENY" always;
add_header Content-Security-Policy "frame-ancestors 'none'" always;
```

### Best Practices
1. **Use CSP over X-Frame-Options**: More flexible and modern
2. **Test All Sensitive Pages**: Ensure headers are applied consistently
3. **Monitor Headers**: Use tools like securityheaders.com
4. **Defense in Depth**: Combine multiple security measures
5. **Regular Audits**: Check for header regression in deployments

## Real-World Impact

### Financial Consequences
- **Unauthorized Transfers**: Victims unknowingly authorize payments
- **Account Takeover**: Attackers change account settings
- **Identity Theft**: Access to sensitive financial information

### Business Impact
- **Regulatory Fines**: Violation of financial security regulations
- **Customer Trust**: Loss of confidence in security measures
- **Legal Liability**: Responsibility for fraudulent transactions
- **Reputation Damage**: Public disclosure of security vulnerabilities

## Testing Tools

### Automated Scanners
- **OWASP ZAP**: Free security testing proxy
- **Burp Suite**: Professional web security testing
- **Mozilla Observatory**: Free online header scanner
- **Security Headers**: Online header analysis tool

### Manual Testing
```bash
# Check headers
curl -I https://target.com/sensitive-page

# Test iframe embedding
echo '<iframe src="https://target.com/sensitive-page"></iframe>' > test.html
open test.html
```

### Browser Developer Tools
1. **Network Tab**: Check response headers
2. **Console**: Look for iframe blocking messages
3. **Elements**: Inspect iframe loading status
4. **Security**: Review page security indicators

## Related Vulnerabilities

1. **UI Redressing** (CWE-1021)
2. **Cross-Frame Scripting** (CWE-346)
3. **Session Fixation** (CWE-384)
4. **Cross-Site Request Forgery** (CWE-352)

## References

- [OWASP Clickjacking Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html)
- [MDN X-Frame-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options)
- [MDN CSP frame-ancestors](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/frame-ancestors)
- [Security Headers Scanner](https://securityheaders.com/)
- [OWASP Top 10 2021 - A05 Security Misconfiguration](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)

## Lab Information

- **Port**: 5011
- **Technology**: Flask, Python, HTML5, CSS3, JavaScript
- **Difficulty**: Beginner to Intermediate
- **Time Required**: 20-30 minutes
- **Prerequisites**: Basic understanding of HTTP headers and web security