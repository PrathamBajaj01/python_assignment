from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ..schemas.product_schema import ProductSchema
from ..services.product_service import ProductService

products_bp = Blueprint("products", __name__)
_schema = ProductSchema()

@products_bp.route("/", methods=["POST"])
def create_product():
    json_data = request.get_json(silent=True) or {}
    try:
        data = _schema.load(json_data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    created = ProductService.create(data)
    return jsonify(created), 201

@products_bp.route("/<product_id>", methods=["GET"])
def get_product(product_id):
    res = ProductService.get(product_id)
    if not res:
        return jsonify({"error": "not found"}), 404
    return jsonify(res)

@products_bp.route("/<product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    json_data = request.get_json(silent=True) or {}
    try:
        data = _schema.load(json_data, partial=True)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    updated = ProductService.update(product_id, data)
    if not updated:
        return jsonify({"error": "not found"}), 404
    return jsonify(updated)

@products_bp.route("/", methods=["GET"])
def list_products():
    return jsonify(ProductService.list_all())
