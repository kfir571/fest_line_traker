import os
from flask_cors import CORS

def _cors_origins():
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [o.strip() for o in raw.split(",") if o.strip()]

def create_app():
    app = Flask(__name__)
    CORS(app, origins=_cors_origins())
    return app
