import os
from flask import Flask
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 1024  

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Ensure temp dirs exist
    os.makedirs("tmp", exist_ok=True)
    os.makedirs("downloads", exist_ok=True)

    return app

app = create_app()