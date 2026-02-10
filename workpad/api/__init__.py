from flask import Flask
from .errors import errors_bp
from .routes import bp as api_bp

def create_app(config_object=None):
    app = Flask(__name__)
    
    if config_object:
        app.config.from_object(config_object)
        
    app.register_blueprint(errors_bp)
    app.register_blueprint(api_bp)
    
    return app
