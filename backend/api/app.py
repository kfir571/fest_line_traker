from api import create_app
from flask_cors import CORS

app = create_app()
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}})


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8000, debug=True)
