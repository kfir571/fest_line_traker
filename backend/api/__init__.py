import os
from flask import Flask
from flask_cors import CORS
from api.routes_analytics import analytics_bp  

def _cors_origins():
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [o.strip() for o in raw.split(",") if o.strip()]

def create_app():
    app = Flask(__name__)
    CORS(app, origins=_cors_origins())

    app.register_blueprint(analytics_bp, url_prefix="/api") 
    return app
