from flask import Flask
from flask_cors import CORS
from .routes import main_bp
from .config import load_config

def create_app():
    app = Flask(__name__)
    
    # Carregar configurações
    load_config(app)
    
    # Configurar CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    
    return app
