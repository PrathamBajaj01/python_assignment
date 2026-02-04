from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.schemas.order_schema import OrderSchema
from app.services.order_service import OrderService

orders_bp = Blueprint("orders", __name__)
schema = OrderSchema()


@orders_bp.route("/", methods=["POST"])
def create_order():
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    return jsonify(OrderService.create(data)), 201


@orders_bp.route("/<order_id>", methods=["GET"])
def get_order(order_id):
    result = OrderService.get(order_id)
    if not result:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@orders_bp.route("/<order_id>", methods=["PUT", "PATCH"])
def update_order(order_id):
    try:
        data = schema.load(request.get_json(), partial=True)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    updated = OrderService.update(order_id, data)
    if not updated:
        return jsonify({"error": "not found"}), 404
    return jsonify(updated)


@orders_bp.route("/customer/<customer_id>/history", methods=["GET"])
def customer_history(customer_id):
    return jsonify(OrderService.order_history(customer_id))
