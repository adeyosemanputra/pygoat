# Contributing to A09 Labs

This document explains how to add new labs under **OWASP Top 10:2025 – A09** by following the same technical structure used in the **Silent Privilege Escalation** lab. This guide describes *how things are wired*, not *why they exist*.

---

## A09 Directory Layout

All A09 content lives under:

**dockerized_labs/owasp_2025/a09/**

The directory contains:

- **docker-compose.yml** – launches A09 services  
- **index/** – A09 landing page  
- **shared/** – shared UI assets  
- **silent_privilege_escalation/** – reference lab  

New labs must be added at the same level as `silent_privilege_escalation`.

---

## Adding a New A09 Lab

To add a new lab:

1. Create a new directory under the A09 root.  
2. Use `silent_privilege_escalation` as the reference structure.  
3. Rename files and directories to match the new lab.  

A typical lab directory contains:

- `app.py`  
- `Dockerfile`  
- `requirements.txt`  
- `README.md`  
- `solution.md`  
- `templates/`  

---

## Shared Components

All A09 labs reuse shared UI components from:

- **shared/templates/base.html**  
- **shared/static/css/style.css**

Each lab template should extend `base.html`.  
Shared files must not be duplicated inside individual lab directories.

---

## A09 Index

The **index/** directory provides the A09 entry page. Its responsibility is limited to:

- listing A09 labs  
- linking to running lab instances  

No lab logic or vulnerabilities should be implemented here.

---

## Docker Integration

Each lab runs as an independent Docker container. For every new lab:

- add a `Dockerfile` inside the lab directory  
- expose port `5000` inside the container  
- add a new service entry in A09’s `docker-compose.yml`  
- map a unique host port to container port `5000`  

---

## Lab Application Structure

Each lab runs its own Flask application.  
The Silent Privilege Escalation lab demonstrates the standard pattern:

- session-based authentication  
- lab-specific routes  
- logging and alert helpers  
- vulnerable and secure behavior in the same app  

New labs may reuse this structure and remove unused logic.

---

## Templates

Common templates used in Silent Privilege Escalation:

- **index.html** – lab entry and login  
- **dashboard.html** – main interaction page  
- **audit.html** – audit log view (optional)  
- **secure-fix.html** – secure-mode explanation (optional)  

New labs may add or remove templates as required.

---

## Documentation Files

Each A09 lab should include:

### README.md

Contains:

- lab overview  
- startup instructions  
- access URL  
- success condition  

Exploit details should not be included.

---

### solution.md

Contains:

- full exploit walkthrough  
- explanation of hints  
- secure-mode comparison  

This file may contain spoilers.

---

## Summary

To add a new A09 lab:

- create a new lab directory under A09  
- follow the structure of Silent Privilege Escalation  
- reuse shared templates and static assets  
- add a Docker service entry  
- keep lab logic self-contained  
- include `README.md` and `solution.md`  

The Silent Privilege Escalation lab is the reference implementation for A09.
