import os

from api.routes import api_bp
from flask import Flask


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.after_request
    def add_cors_headers(response):
        # Lightweight CORS helper so the frontend can run from a static file server during prototyping.
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return response

    return app


app = create_app()


if __name__ == "__main__":
    # Enable debug for development convenience; turn off in production.
    port = int(os.environ.get("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=True)
