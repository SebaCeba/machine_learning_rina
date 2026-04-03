from flask import Flask
import os

def create_app():
    # Specify template folder relative to project root
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    
    app.config['UPLOAD_FOLDER'] = 'data'
    app.config['MODEL_FOLDER'] = 'models'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)
    
    from app import routes_simple
    app.register_blueprint(routes_simple.bp)
    
    return app
