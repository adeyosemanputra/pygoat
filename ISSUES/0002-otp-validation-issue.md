<!-- Use this template to report the OTP lab behavior seen while testing with Burp Intruder.
Fill the sections below with exact requests, responses and Intruder settings so maintainers can reproduce. -->

# OTP lab: Intruder brute-force / verification discrepancy

**Reporter:** (your name)
**Date:** 2026-02-02
**Affected lab/app:** `introduction` app — OTP flow (views: `login_otp`, `Otp`)

---


## Short summary

While testing the OTP flow I attempted to brute-force the OTP with Burp Intruder. None of the digit payloads returned a true/positive response according to my match condition, but I later discovered the correct solution. This report captures reproduction steps, Intruder settings, and suggested fixes.

---


## Files of interest

- `introduction/views.py` — `login_otp`, `Otp` (OTP generation and verification logic)
- `introduction/urls.py` — routes for `login_otp` and `otp`

---


## Reproduction steps (include exact request/response + Intruder config)

1. Start from the OTP request page: `GET /login_otp` and capture the flow.
2. Request an OTP for an email (example): `POST /otp` with form field `email=tester@example.com` — capture the full request.
3. Save the generated request you used for brute-forcing (example payload position marked with `§` in the raw request). Paste the raw HTTP request below.
4. Burp Intruder configuration used:
	- Position(s): e.g., the single numeric digit in parameter `otp` or the request body value `otp=§`.
	- Payload set: `0-9` (digits) or custom list you used.
	- Attack type: Sniper / Cluster bomb
	- Matcher: (response length / status / string). Paste the match condition here.
5. Run Intruder and record results. Paste the raw responses or summary (rows that looked like "true" / "match"), or state "none matched".

Paste captured HTTP request (raw):
```
<PASTE RAW HTTP REQUEST HERE, include headers and body>
```

Paste the Intruder payload positions and payload list (or attach payload file):

---

---


## Observed behavior

- Intruder results: (e.g. "no response matched my matcher; none returned true")
- Application behavior: (e.g. OTP printed to template/console, or verification allowed login)
- Any console output / server logs (paste verbatim).

If you already found the correct OTP or exploit details, paste them in the "Solution / Findings" section below — do not include proofs in production logs.

---


## Expected behavior

The server should:
- Generate adequately random OTPs (sufficient length and entropy).
- Not expose the OTP in templates or logs during normal operation.
- Store an OTP tied to the user/email with a timestamp and single-use enforcement.
- Verify submitted OTPs only against the matching user's stored OTP and return a clear failure on mismatch.

---


## Root cause / findings (initial)

Preliminary code review indicates:

- OTP generation uses `randint(100,103)` (very small, predictable space).
- OTPs are stored via `otp.objects.update_or_create(id=...)` (may not be scoped per-email/user).
- Code prints OTPs and renders them into templates during testing (`print(otpN)` and `render(..., {"otp": otpN})`).
- No expiry timestamp or single-use check is enforced in the logic.

These points lead to both weak OTP entropy and potential verification mismatches or leaks.

---


## Suggested fixes

- Increase OTP entropy (e.g., 6-digit numeric or longer, generated using `secrets.randbelow` or equivalent secure RNG).
- Tie OTP records to the requesting user's email or user ID; use per-user storage rather than a hard-coded `id=1`/`id=2`.
- Add expiry timestamp and single-use invalidation.
- Remove printing or rendering of OTP in templates; deliver via email/SMS (out-of-band).
- Harden verification logic to explicitly compare the stored OTP for that email and return 403/401 on mismatch.
- Add automated tests for brute-force resistance, expiry, and single-use behavior.

---


## Environment

- OS: Windows
- Python: (version)
- Django: (version)
- Database: sqlite3

---

## Solution / Findings (your confirmed solution)

If you have already found the correct OTP or a bypass, paste the minimal reproduction here (steps + exact payload). If you prefer not to share the exact OTP in public, indicate that a fix was found and include a private note or attach it to the PR.

---

## PoC / Attachments

- Paste raw request/response snippets that demonstrate the behavior.
- Include Intruder payload file or screenshots if useful.

---

## Next steps

1. Attach the raw requests/responses and Intruder settings above.  
2. I will prepare a small patch to replace `randint(100,103)` with a secure generator, scope OTPs per-email, and add expiry + single-use checks.  
3. Create a PR referencing this issue with tests.

---

## Status

- Created locally: yes
- Created on tracker: no


---

## Next Steps

1. Add a concise reproduction case and paste console output here.  
2. Implement fixes in `introduction/views.py` (generate secure OTP, add expiry, avoid printing).  
3. Create a PR referencing this issue with tests.

---

## Status

- Created locally: yes
- Created on tracker: no
