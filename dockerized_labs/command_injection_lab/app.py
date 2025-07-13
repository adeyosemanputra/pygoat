from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

@app.route('/')
def index():
    """Main page with command injection lab description"""
    return render_template('index.html')

@app.route('/lab1', methods=['GET', 'POST'])
def lab1():
    """Lab 1: Name Server Lookup with Command Injection"""
    if request.method == 'POST':
        domain = request.form.get('domain', '')
        os_type = request.form.get('os', '')
        
        if os_type == 'win':
            command = f"nslookup {domain}"
        else:
            command = f"dig {domain}"
        
        try:
            # Intentionally vulnerable command execution
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            output = stdout.decode('utf-8') + stderr.decode('utf-8')
        except Exception as e:
            output = str(e)
            
        return render_template('lab1.html', output=output)
    
    return render_template('lab1.html')

@app.route('/lab2', methods=['GET', 'POST'])
def lab2():
    """Lab 2: Python eval() Code Execution"""
    if request.method == 'POST':
        try:
            # Intentionally vulnerable eval
            expression = request.form.get('val', '')
            output = eval(expression)
            return render_template('lab2.html', output=str(output))
        except Exception as e:
            return render_template('lab2.html', output=str(e))
    
    return render_template('lab2.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5013, debug=True)
