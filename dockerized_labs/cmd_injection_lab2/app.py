import ast
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Command Injection Lab 2 – {{ mode.title() }} Mode</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(to right, #e0f7fa, #fff);
            font-family: 'Segoe UI', sans-serif;
        }
        .lab-container {
            max-width: 650px;
            background: #ffffff;
            padding: 2rem 2.5rem;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .btn-group .btn {
            min-width: 120px;
        }
        input[type="text"] {
            height: 50px;
            font-size: 1.1rem;
        }
        pre {
            background: #f8f9fa;
            padding: 1rem;
            border-left: 5px solid #0d6efd;
            font-size: 1rem;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="d-flex justify-content-center align-items-center min-vh-100">
        <div class="lab-container">
            <h3 class="text-center mb-4">
                🧪 Command Injection Lab 2<br>
                <small class="text-muted">{{ mode.title() }} Mode</small>
            </h3>

            <form method="post">
                <input type="text" class="form-control mb-3" name="val" value="{{ val or '' }}" placeholder="Try: 7 * 7 or __import__('os').system('whoami')">
                <div class="text-center btn-group">
                    <button class="btn btn-primary" type="submit">▶️ Run</button>
                    <a href="/safe" class="btn btn-success {% if mode == 'safe' %}active{% endif %}">🛡️ Safe Mode</a>
                    <a href="/unsafe" class="btn btn-danger {% if mode == 'unsafe' %}active{% endif %}">⚠️ Unsafe Mode</a>
                </div>
            </form>

            {% if output %}
            <div class="mt-4">
                <h5>📤 Output:</h5>
                <div class="bg-white p-3 border rounded">{{ output|safe }}</div>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''


def safe_math_eval(expr):
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.Constant  # Python 3.8+
    )

    try:
        node = ast.parse(expr, mode='eval')
        if not all(isinstance(n, allowed_nodes) for n in ast.walk(node)):
            raise ValueError("Disallowed expression")
        return eval(compile(node, "<safe>", mode="eval"))
    except Exception:
        raise ValueError("Only basic math expressions are allowed.")


@app.route("/")
def index():
    return redirect("/safe")


@app.route("/safe", methods=["GET", "POST"])
def safe():
    val = ""
    output = ""
    if request.method == "POST":
        val = request.form.get("val")
        try:
            output = safe_math_eval(val)
        except Exception:
            output = (
                "❌ Unsafe input detected!<br>"
                "In <strong>Safe Mode</strong>, only basic math expressions are allowed.<br><br>"
                "✅ Try something like: <code>7 + 3</code>, <code>5 * (2 + 1)</code><br>"
                "🚫 Avoid: <code>__import__('os')</code>, function calls, or modules."
            )

    return render_template_string(HTML_TEMPLATE, output=output, val=val, mode="safe")


@app.route("/unsafe", methods=["GET", "POST"])
def unsafe():
    val = ""
    output = ""
    if request.method == "POST":
        val = request.form.get("val")
        try:
            output = eval(val)  # Deliberately vulnerable
        except Exception as e:
            output = f"Error: {e}"
    return render_template_string(HTML_TEMPLATE, output=output, val=val, mode="unsafe")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
