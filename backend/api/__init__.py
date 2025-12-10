from flask import Flask
from backend.api.routes_analytics import analytics_bp


def create_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(analytics_bp, url_prefix="/api")

    return app
