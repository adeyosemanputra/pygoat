# A09 – Silent Privilege Escalation (Solution Walkthrough)

⚠️ **Spoiler Warning**

This document explains the intended solution and reasoning path
for the Silent Privilege Escalation lab.
Read this only after attempting the lab on your own.

---

## 1. What the Lab Was Designed to Teach

This lab is not about missing authentication or broken access control.
It demonstrates a more subtle failure:

> Security logging and alerting exist, but can be bypassed under certain conditions.

The system records events correctly, yet fails to raise alerts when a
privilege escalation succeeds through a trusted execution path.

This is a classic **OWASP A09** failure.

---

## 2. Initial Observation (Baseline Security Works)

When a normal user attempts to change their role using the dashboard UI:

- The role does **not** change
- A log entry is created
- The user receives feedback that the request was recorded
- In some cases, a security alert is raised

At this stage, the learner should conclude:

- Logging exists
- Alerting exists
- Simple attempts are detected

This establishes that the system is not trivially broken.

---

## 3. Interpreting the Early Hints

During failed attempts, the application provides a conceptual hint:

> “Some requests are treated as more trusted than others.”

This hint is intentionally vague.
It does not mention parameters, headers, or specific fields.

The correct interpretation is:

- The system is classifying requests
- Trust is being inferred from request context
- Authorization and alerting behavior depends on that classification

This shifts the mindset from *role-based thinking* to *context-based thinking*.

---

## 4. Identifying the Core Design Flaw

In Vulnerable Mode, the backend makes a critical assumption:

- Certain requests are considered “internal” or trusted
- Those requests are allowed to perform sensitive actions
- Alerts are suppressed for these trusted workflows

The flaw is not logging.
The flaw is **trusting the presence of client-supplied context** to decide:

- whether an action is authorized
- whether an alert should fire

The system assumes the attacker cannot influence this context.

---

## 5. Exploitation Logic (How the Escalation Worked)

The exploit succeeds when:

1. The same role-change request is sent
2. Additional context is included that causes the backend to treat it as internal
3. Authorization and alerting checks are skipped
4. The role change succeeds silently
5. Logs still record the event

Importantly:

- The specific value of the context is not what matters
- The **presence** of a trusted signal is enough

This mirrors real-world failures where internal flags, workflow markers,
or automation signals are trusted without verification.

---

## 6. Alternative Attacker Reasoning Paths

An attacker does not need to know the exact keyword in advance.

Common experimentation patterns include trying signals such as:

- internal(try sending &internal=true alongside role using tools like burp)
- trusted
- automation
- system
- service
- workflow indicators

These names are frequently used in real systems to differentiate
user-initiated actions from internal processes.

The key takeaway:
> If a system trusts client-supplied context to infer authority,
it can be manipulated.

---

## 7. Why No Alert Was Raised

The alerting logic in Vulnerable Mode was conditional.

- Failed attempts were treated as suspicious
- Successful internal-classified actions were treated as expected
- Alerts were tied to outcome, not intent

As a result:

- A high-risk action succeeded
- Logs captured the event
- No alert was triggered

This is a textbook **Security Logging and Alerting Failure**.

---

## 8. Secure Mode Comparison

In Secure Mode, the system behavior changes:

- Authorization is enforced based on server-side identity
- Client-supplied context is ignored for trust decisions
- Privilege escalation attempts always trigger alerts
- Success or failure does not affect detection

This demonstrates the correct design pattern.

---

## 9. Real-World Parallels

Similar failures have occurred in real environments where:

- Internal automation endpoints shared code paths with user-facing systems
- Alerting was suppressed for “trusted” services
- Privilege changes were logged but not escalated
- CI/CD or provisioning systems relied on request flags instead of identity

In many cases, attackers did not disable logging.
They simply bypassed detection logic.

---

## 10. Key Takeaways

- Logging without alerting creates a false sense of security
- Trust should never be inferred from client-controlled context
- High-risk actions must be monitored based on intent
- Secure design enforces authorization independently of workflow
- Detection should not depend on whether an action succeeds

---

## End of Solution

If you were able to reason through the exploit without this guide,
you successfully demonstrated attacker-level thinking aligned with
real-world A09 failures.
