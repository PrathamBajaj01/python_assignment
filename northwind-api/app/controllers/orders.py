from flask import Blueprint, request, jsonify
from ..schemas.order_schema import OrderSchema
from ..services.order_service import OrderService
from marshmallow import ValidationError

orders_bp = Blueprint("orders", __name__)
schema = OrderSchema()

@orders_bp.route("/", methods=["POST"])
def create_order():
    json_data = request.get_json()
    try:
        data = schema.load(json_data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    created = OrderService.create(data)
    return jsonify(created), 201

@orders_bp.route("/<order_id>", methods=["GET"])
def get_order(order_id):
    res = OrderService.get(order_id)
    if not res:
        return jsonify({"error": "not found"}), 404
    return jsonify(res)

@orders_bp.route("/<order_id>", methods=["PUT", "PATCH"])
def update_order(order_id):
    json_data = request.get_json()
    try:
        data = schema.load(json_data, partial=True)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    updated = OrderService.update(order_id, data)
    if not updated:
        return jsonify({"error": "not found"}), 404
    return jsonify(updated)

@orders_bp.route("/customer/<customer_id>/history", methods=["GET"])
def customer_history(customer_id):
    history = OrderService.order_history(customer_id)
    return jsonify(history)
