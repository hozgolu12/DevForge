from flask import Flask, request
import time
from app.config import Config
from app.logger import logger
from app.routes import routes_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Middleware: Request Logging
    @app.before_request
    def start_timer():
        request.start_time = time.time()

    @app.after_request
    def log_request(response):
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time
            logger.info(
                f"{request.method} {request.path} {response.status_code}",
                extra={
                    "ip": request.remote_addr,
                    "duration": duration,
                }
            )
        return response

    # Register Blueprint
    app.register_blueprint(routes_bp)

    return app
