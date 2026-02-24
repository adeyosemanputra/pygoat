from flask import request, g

def init_lab(app):
    @app.before_request
    def detect_base_path():
        g.base_path = request.headers.get('X-Script-Name', '')

    @app.context_processor
    def inject_base_path():
        return {'base_path': g.base_path}
