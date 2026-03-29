# Business Logic Flaws - Discount Abuse Lab

## Overview

This lab demonstrates a critical business logic vulnerability where an e-commerce application fails to properly validate discount coupon applications, allowing attackers to abuse the system and reduce purchase prices to nearly zero.

## Vulnerability Details

- **Vulnerability Type**: Business Logic Flaw - Discount Abuse
- **Severity**: High
- **OWASP Category**: A04:2021 - Insecure Design
- **CWE**: CWE-840 (Business Logic Errors)

## Lab Scenario

You're testing an online electronics store that offers discount coupons during checkout. The application has a critical flaw in its business logic that allows customers to apply the same discount coupon multiple times, leading to compound discounts that can reduce the total price below cost.

### Story
- **Setting**: PyGoat Electronics Store
- **Initial Cart Value**: ₹1000+ (smartphone, laptop, headphones)
- **Available Coupons**: 
  - `DISCOUNT10` - 10% off any order
  - `SAVE20` - 20% off orders over ₹500
- **Goal**: Reduce total cost below ₹100

## Exploitation

### Step-by-Step Attack

1. **Setup the Cart**
   - Navigate to `/store`
   - Add products to reach ₹1000+ total
   - Go to cart (`/cart`)

2. **Apply Discount Coupons**
   - Enter `DISCOUNT10` in the coupon field
   - Click "Apply Coupon"
   - Notice the 10% discount is applied

3. **Exploit the Flaw**
   - Apply the same coupon (`DISCOUNT10`) again
   - Observe that it applies another 10% discount
   - Continue applying until total is below ₹100

4. **Mathematical Progression**
   ```
   Starting: ₹1000
   1st application: ₹1000 - (10% of ₹1000) = ₹900
   2nd application: ₹900 - (10% of ₹900) = ₹810
   3rd application: ₹810 - (10% of ₹810) = ₹729
   ...continues until below ₹100
   ```

### Expected Results
- After 10-15 applications of DISCOUNT10, the total should be below ₹100
- The application allows unlimited coupon applications
- Each application compounds the discount

## Vulnerable Code Analysis

### The Problem
```python
# VULNERABLE: Always allows coupon application
else:
    session['applied_coupons'].append(coupon_code)
    session.modified = True
    return jsonify({
        'success': True, 
        'message': f'Coupon {coupon_code} applied successfully!'
    })
```

### What Makes It Vulnerable
1. **No Validation**: No check if coupon already applied
2. **State Mismanagement**: Just appends to list without validation
3. **Business Logic Bypass**: Allows unlimited applications
4. **Compound Effect**: Each application reduces remaining total

## Secure Implementation

### Fixed Code
```python
# SECURE: Check if coupon already applied
if coupon_code not in session['applied_coupons']:
    session['applied_coupons'].append(coupon_code)
    session.modified = True
    return jsonify({
        'success': True, 
        'message': f'Coupon {coupon_code} applied successfully!'
    })
else:
    return jsonify({
        'success': False, 
        'message': f'Coupon {coupon_code} has already been applied to this order.'
    })
```

### Additional Security Measures

1. **Database-Backed Validation**
```python
class AppliedCoupons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), nullable=False)
    coupon_code = db.Column(db.String(20), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('order_id', 'coupon_code'),
    )
```

2. **Server-Side Business Rules**
```python
def validate_coupon_application(order_id, coupon_code):
    existing = db.query(AppliedCoupons).filter_by(
        order_id=order_id, 
        coupon_code=coupon_code
    ).first()
    
    if existing:
        raise ValidationError("Coupon already applied to this order")
    return True
```

3. **Rate Limiting and Monitoring**
```python
# Implement rate limiting for coupon applications
# Log all coupon usage for fraud detection
# Set maximum discount thresholds
```

## Lab Features

### Secure Mode Toggle
The lab includes a "Secure Mode" feature that demonstrates proper implementation:
- Toggle between vulnerable and secure modes
- Compare behavior in both modes
- Understand the difference in validation logic

### Real-Time Feedback
- Live cart total updates
- Coupon application feedback
- Challenge completion status
- Applied coupons tracking

## Testing Instructions

### Manual Testing
1. Start the application: `docker-compose up`
2. Navigate to `http://localhost:5010`
3. Follow the lab instructions
4. Test both vulnerable and secure modes

### Automated Testing
```bash
# Test vulnerable mode
curl -X POST http://localhost:5010/apply_coupon \
  -d "coupon_code=DISCOUNT10" \
  -c cookies.txt -b cookies.txt

# Apply same coupon multiple times
for i in {1..10}; do
  curl -X POST http://localhost:5010/apply_coupon \
    -d "coupon_code=DISCOUNT10" \
    -c cookies.txt -b cookies.txt
done
```

## Prevention & Mitigation

### Developer Guidelines
1. **Server-Side Validation**
   - Always validate business rules on the server
   - Never trust client-side validation alone
   - Implement comprehensive input validation

2. **State Management**
   - Use database constraints for business rules
   - Implement proper transaction management
   - Track all state changes with audit logs

3. **Business Logic Testing**
   - Test all edge cases and negative scenarios
   - Validate business rules under various conditions
   - Implement comprehensive unit and integration tests

4. **Monitoring and Alerting**
   - Log all significant business actions
   - Implement fraud detection mechanisms
   - Set up alerts for unusual patterns

### Security Controls
- Input validation and sanitization
- Business rule enforcement
- Transaction integrity checks
- Rate limiting and throttling
- Comprehensive audit logging
- Real-time fraud detection

## Real-World Impact

### Financial Consequences
- **Direct Revenue Loss**: Customers purchasing items for free or minimal cost
- **Inventory Losses**: Products sold below cost price
- **Operational Costs**: Manual review and correction of fraudulent orders

### Business Impact
- **Reputation Damage**: Customer trust and brand reputation
- **Compliance Issues**: Violation of business policies and regulations
- **Competitive Disadvantage**: Unfair pricing affecting market position

## Related Vulnerabilities

1. **Price Manipulation** (CWE-840)
2. **Insufficient Process Validation** (CWE-841)
3. **Race Conditions** (CWE-362)
4. **Improper Input Validation** (CWE-20)

## References

- [OWASP Top 10 2021 - A04 Insecure Design](https://owasp.org/Top10/A04_2021-Insecure_Design/)
- [CWE-840: Business Logic Errors](https://cwe.mitre.org/data/definitions/840.html)
- [OWASP Testing Guide - Business Logic Testing](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/10-Business_Logic_Testing/)

## Lab Information

- **Port**: 5010
- **Technology**: Flask, Python
- **Difficulty**: Beginner
- **Time Required**: 15-30 minutes
- **Prerequisites**: Basic understanding of web applications and HTTP requests