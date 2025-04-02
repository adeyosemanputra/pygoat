import ast
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = '''
<title>Command Injection Lab 2</title>
<h3 align="center">Evaluate any expression!</h3>
<form method="post">
    <label><b>Safe Mode:</b></label>
    <select name="mode">
        <option value="on" {% if mode == 'on' %}selected{% endif %}>ON (Safe)</option>
        <option value="off" {% if mode == 'off' %}selected{% endif %}>OFF (Vulnerable)</option>
    </select>
    <br><br>

    <input type="text" name="val" value="{{ val or '' }}" placeholder="e.g., 7 * 7"><br><br>
    <center><button type="submit">GO</button></center>
</form>

{% if output %}
<h4>Output</h4>
<pre>{{ output }}</pre>
{% endif %}
'''


@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    val = ""
    mode = "off"  # default is vulnerable

    if request.method == "POST":
        val = request.form.get("val", "")
        mode = request.form.get("mode", "off")

        try:
            if mode == "on":
                output = ast.literal_eval(val)  # SAFE
            else:
                output = eval(val)  # UNSAFE
        except Exception as e:
            output = f"Error: {e}"

    return render_template_string(HTML, output=output, val=val, mode=mode)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
