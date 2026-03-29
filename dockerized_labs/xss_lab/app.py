from flask import Flask, render_template, request

app = Flask(__name__)
comments_store = []

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'POST':
        comment = request.form.get('comment', '')
        if comment:
            comments_store.append(comment)
    
    return render_template('comments.html', comments=comments_store)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
