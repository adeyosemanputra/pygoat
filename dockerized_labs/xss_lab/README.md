# XSS (Cross-Site Scripting) Lab

This lab demonstrates different types of Cross-Site Scripting (XSS) vulnerabilities. It is designed for educational purposes to help users understand how XSS attacks work and how to prevent them.

## Vulnerabilities Demonstrated

1. **Reflected XSS**: Demonstrates how user input is immediately returned and displayed
2. **Stored XSS**: Shows partial filter bypass using alternative payloads
3. **DOM XSS**: Illustrates XSS through alphanumeric filtering bypass

## Setup Instructions

1. Install Docker and Docker Compose
2. Clone this repository
3. Run `docker-compose up --build`

### Manual Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```
4. Access the lab at http://localhost:5006

## Lab Exercises

### Lab 1: Reflected XSS
- Enter different FAANG company names to see legitimate output
- Try entering HTML/JavaScript code to see if it gets reflected

### Lab 2: Stored XSS with Simple Filter
- Submit comments that will be stored and displayed
- Try to bypass the basic script tag filter

### Lab 3: DOM XSS with Character Filter
- Input gets filtered to remove alphanumeric characters
- Challenge: Execute JavaScript without using regular letters/numbers

## Warning

This is a deliberately vulnerable application designed for learning web security concepts. DO NOT deploy to production or expose to the internet.
