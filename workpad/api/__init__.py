from flask import Flask
from flask_cors import CORS
from ..config import settings
from .errors import errors_bp
from .routes import bp as api_bp

def create_app(config_object=None):
    # Configure logging first
    settings.configure_logging()
    
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": settings.CORS_ORIGINS}})
    
    if config_object:
        app.config.from_object(config_object)
        
    app.register_blueprint(errors_bp)
    app.register_blueprint(api_bp)
    
    return app
