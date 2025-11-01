from flask import Flask, render_template, request, redirect, url_for, render_template_string
import os
import uuid

app = Flask(__name__)

# Directory to store blog posts
BLOG_DIR = os.path.join(app.root_path, 'templates', 'blogs')
os.makedirs(BLOG_DIR, exist_ok=True)

def create_blog_post(title, content):
    """Create a new blog post with the given title and content."""
    # Generate a unique filename using UUID
    filename = f"{uuid.uuid4()}.html"
    filepath = os.path.join(BLOG_DIR, filename)
    
    # Create the blog post template
    blog_template_content = f'''
{{% extends "base.html" %}}
{{% block title %}}{ title }{{% endblock %}}
{{% block content %}}
<div class="box">
    <h3>{ title }</h3>
    <div class="content">
        { content }
    </div>
</div>
{{% endblock %}}
'''
    
 
    # rendered_blog = render_template_string(blog_template_content, title=title, content=content)

    # Write the blog post to file
    with open(filepath, 'w') as f:
        f.write(blog_template_content )
    
    return filename

def get_blog_posts():
    """Get a list of all blog posts."""
    posts = []
    if os.path.exists(BLOG_DIR):
        for filename in os.listdir(BLOG_DIR):
            if filename.endswith('.html'):
                filepath = os.path.join(BLOG_DIR, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Extract title from the template
                    title = content.split('<h3>')[1].split('</h3>')[0] if '<h3>' in content else 'Untitled'
                    posts.append({
                        'filename': filename,
                        'title': title
                    })
    return posts

@app.route('/')
def index():
    """Display the main lab page with instructions."""
    return render_template('index.html')

@app.route('/lab')
def lab():
    """Display the lab page with blog creation form and list of posts."""
    posts = get_blog_posts()
    return render_template('lab.html', posts=posts)

@app.route('/create_blog', methods=['POST'])
def create_blog():
    """Handle blog post creation."""
    title = request.form.get('title', 'Untitled')
    content = request.form.get('content', '')
    
    # Patched the vulnerability: user input is no longer rendered as a template.
    try:
        # Create the blog post with the user's content directly
        filename = create_blog_post(title, content)
        return redirect(url_for('view_blog', filename=filename))
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/blog/<filename>')
def view_blog(filename):
    """View a specific blog post."""
    try:
        return render_template(f'blogs/{filename}')
    except Exception as e:
        return f"Blog post not found: {str(e)}", 404

@app.route('/toggle-theme')
def toggle_theme():
    """Toggle between light and dark theme."""
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5015, debug=True)
