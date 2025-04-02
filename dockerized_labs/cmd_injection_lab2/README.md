# 🧪 Command Injection Lab 2 – Dockerized

This is a standalone, intentionally vulnerable lab demonstrating **Python's `eval()` vulnerability**, extracted from the [OWASP PyGoat](https://github.com/adeyosemanputra/pygoat) project.

It shows how command/code injection can occur through unsanitized user input, and how to mitigate it using Python's `ast.literal_eval()`.

---

## 🚀 How to Run (Docker)

```bash
docker build -t cmd-injection-lab2 .
docker run -p 5000:5000 cmd-injection-lab2
```

Then open: [http://localhost:5000](http://localhost:5000)

---

## 🔥 Features

- `eval()` vulnerability for code injection demo  
- 🔄 Toggle between **Safe Mode** (`ast.literal_eval`) and **Vulnerable Mode** (`eval`)  
- Input persists after submission  
- Fully Dockerized for safe testing  

---

## 💣 Example Payloads

```python
7 + 7
__import__('os').system('whoami')
__import__('os').system('dir')
```

---

## ⚠️ Disclaimer

> This is for educational purposes **only**.  
> Do **NOT** deploy in production environments.

---

🛠️ Contributed for [Issue #237](https://github.com/adeyosemanputra/pygoat/issues/237)  
✨ Author: [@mahii-17](https://github.com/mahii-17)
