from flask import Flask, jsonify
import logging
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(level=Config.LOG_LEVEL)
    logger = logging.getLogger("northwind-api")
    logger.info("Northwind API starting")

    # register blueprints
    from .controllers.customers import customers_bp
    from .controllers.products import products_bp
    from .controllers.orders import orders_bp

    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(orders_bp, url_prefix="/orders")

    @app.route("/")
    def hello():
        return jsonify({"ok": True, "service": "northwind-api"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not found"}), 404

    return app
