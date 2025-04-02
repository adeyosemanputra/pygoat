from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('introduction/insec_des.html')

@app.route('/insec_des')
def insec_des():
    return render_template('introduction/insec_des.html')

@app.route('/insec_des_lab')
def insec_des_lab():
    # For now, just show a placeholder message
    return render_template('introduction/insec_des_lab.html', message="Upload logic coming soon...")

if __name__ == '__main__':
    app.run(debug=True)


