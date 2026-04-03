from flask import Flask
from flask_cors import CORS
import os

def create_app():
    # Specify template folder relative to project root
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    
    # Enable CORS for frontend React app
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    app.config['UPLOAD_FOLDER'] = 'data'
    app.config['MODEL_FOLDER'] = 'models'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app import routes
    from app import api_routes
    app.register_blueprint(routes.bp)
    app.register_blueprint(api_routes.api_bp)
    
    return app
