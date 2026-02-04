import os

from api.routes import api_bp
from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Enable CORS for all routes
    CORS(app)

    @app.after_request
    def add_cors_headers(response):
        # Ensure proper CORS headers for preflight requests
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers[
            "Access-Control-Allow-Methods"
        ] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    @app.route("/<path:path>", methods=["OPTIONS"])
    def handle_options(path):
        response = app.response_class()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers[
            "Access-Control-Allow-Methods"
        ] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 200

    return app


app = create_app()


if __name__ == "__main__":
    # Enable debug for development convenience; turn off in production.
    port = int(os.environ.get("PORT", "5001"))
    app.run(
        host="0.0.0.0", port=port, debug=os.environ.get("FLASK_ENV") != "production"
    )
