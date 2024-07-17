from flask import Flask
from flask_cors import CORS
from .routes import main_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey' # substituir no .env
    CORS(app)
    app.register_blueprint(main_bp)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
