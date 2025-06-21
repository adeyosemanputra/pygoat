from flask import Flask, render_template, request, redirect, url_for, flash
import os
import yaml  # Intentionally vulnerable version
from PIL import Image, ImageMath  # Intentionally vulnerable version
import io
import base64  # For converting image to base64 string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
ALLOWED_EXTENSIONS = {'yml', 'yaml', 'jpg', 'png'}

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    logger.info("Accessing index page")
    return render_template('index.html')

@app.route('/lab1')
def lab1():
    return render_template('lab1.html')

@app.route('/lab2')
def lab2():
    return render_template('lab2.html')

@app.route('/get_version')
def get_version():
    versions = {
        'pyyaml': yaml.__version__,
        'pillow': Image.__version__
    }
    return versions

@app.route('/upload_yaml', methods=['POST'])
def upload_yaml():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('lab1'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('lab1'))
    
    if file and allowed_file(file.filename):
        try:
            # Intentionally vulnerable YAML loading
            data = yaml.load(file.stream, Loader=yaml.Loader)
            return render_template('result.html', 
                                content=data, 
                                filename=file.filename)
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            logger.error(f"Error processing YAML file {file.filename}: {str(e)}")
            return redirect(url_for('lab1'))
    
    flash('Invalid file type')
    return redirect(url_for('lab1'))

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        flash('No image file selected')
        return redirect(url_for('lab2'))
    
    file = request.files['image']
    expression = request.form.get('expression', '')
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('lab2'))
    
    if file and allowed_file(file.filename):
        try:
            # Vulnerable image processing using Pillow 8.0.0
            img = Image.open(file)
            img = img.convert("RGB")
            r, g, b = img.split()

            # Intentionally vulnerable expression evaluation
            output = ImageMath.eval(expression, img=img, r=r, g=g, b=b)

            # Save processed image
            buffered = io.BytesIO()
            output.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Save original image for comparison
            buffered_ref = io.BytesIO()
            img.save(buffered_ref, format="JPEG")
            img_str_ref = base64.b64encode(buffered_ref.getvalue()).decode("utf-8")

            return render_template('result.html',
                                image=True,
                                filename=file.filename,
                                img_str=img_str,
                                img_str_ref=img_str_ref)
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            logger.error(f"Error processing image file {file.filename}: {str(e)}")
            return redirect(url_for('lab2'))
    
    flash('Invalid file type')
    return redirect(url_for('lab2'))

if __name__ == '__main__':
    # Ensure we're binding to all interfaces
    app.run(
        host='0.0.0.0',
        port=9000,
        debug=True,
        use_reloader=True,
        threaded=True
    )
