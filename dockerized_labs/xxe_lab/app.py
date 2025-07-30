from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from xml.dom.pulldom import START_ELEMENT, parseString
from xml.sax import make_parser
from xml.sax.handler import feature_external_ges

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    comment = db.Column(db.String(500), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()
    # Add a default comment if none exists
    if not Comment.query.first():
        default_comment = Comment(comment="Welcome! Add your comments here.")
        db.session.add(default_comment)
        db.session.commit()

@app.route('/')
def index():
    """Description page explaining the XXE lab"""
    return render_template('index.html')

@app.route('/lab')
def xxe_lab():
    """Main XXE lab page"""
    return render_template('xxe_lab.html')

@app.route('/see')
def xxe_see():
    """View stored comments"""
    comment = Comment.query.first()
    if comment:
        return render_template('xxe_lab.html', com=comment.comment)
    return render_template('xxe_lab.html')

@app.route('/parse', methods=['POST'])
def xxe_parse():
    """Parse XML input - intentionally vulnerable to XXE"""
    if request.method == "POST":
        try:
            # Create a vulnerable XML parser that allows external entities
            parser = make_parser()
            parser.setFeature(feature_external_ges, True)
            
            # Parse the XML data
            doc = parseString(request.data.decode('utf-8'), parser=parser)
            
            # Extract text from the XML
            for event, node in doc:
                if event == START_ELEMENT and node.tagName == 'text':
                    doc.expandNode(node)
                    text = node.toxml()
                    # Get text between tags
                    start_idx = text.find('>')
                    end_idx = text.find('<', start_idx)
                    text = text[start_idx + 1:end_idx]
                    
                    # Update the comment in database
                    comment = Comment.query.first()
                    if comment:
                        comment.comment = text
                    else:
                        comment = Comment(comment=text)
                        db.session.add(comment)
                    db.session.commit()
                    break
                    
            return render_template('xxe_lab.html')
        except Exception as e:
            print(f"Error parsing XML: {str(e)}")
            return render_template('xxe_lab.html', error="Error processing XML data")

    return render_template('xxe_lab.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
