# A09:2025 – Security Logging & Alerting Failures

This module demonstrates **OWASP Top 10:2025 – A09**, focusing on how inadequate logging, monitoring, and alerting allow attacks to go **undetected**, delaying response and impact assessment.

## Overview
Security Logging & Alerting Failures occur when applications fail to:
- Log security-relevant events correctly
- Protect log integrity
- Monitor logs for suspicious activity
- Trigger alerts for high-risk behaviors

Without effective alerting, attacks may succeed silently and persist for long periods.

## Labs Included
- **Silent Privilege Escalation (No Alert Fired)**  
  A real-world inspired scenario where an attacker escalates privileges successfully **without generating any alerts**, highlighting the risks of insufficient logging and missing detection logic.

> ⚠️ Currently, this is the only lab under A09 and intentionally demonstrates a failure case.


## Starting A09

From the a09 directory, start the application using Docker Compose:
```
docker compose up --build
```

The application will start in the foreground.

---


## Accessing A09

Once the containers are running, access a09 at:
```
http://localhost:5000
```

---

## Stopping 

To stop and shut down containers, press:

```
Ctrl + C
```

## Learning Objectives
- Understand why logging without alerting is insufficient
- Identify security-relevant events that must be logged
- Observe how attacks bypass detection due to missing alerts

## Key Concepts Covered
- Insufficient logging
- Missing alert thresholds
- Lack of real-time detection
- Forensic visibility gaps

## References
- https://owasp.org/Top10/2025/A09_2025-Security_Logging_and_Alerting_Failures/

---
*This module is intentionally vulnerable for educational purposes.*
