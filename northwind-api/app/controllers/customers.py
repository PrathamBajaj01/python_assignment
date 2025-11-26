from flask import Blueprint, request, jsonify
from ..schemas.customer_schema import CustomerSchema
from ..services.customer_service import CustomerService
from marshmallow import ValidationError

customers_bp = Blueprint("customers", __name__)
schema = CustomerSchema()

@customers_bp.route("/", methods=["POST"])
def create_customer():
    json_data = request.get_json()
    try:
        data = schema.load(json_data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    created = CustomerService.create(data)
    return jsonify(created), 201

@customers_bp.route("/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    result = CustomerService.get(customer_id)
    if not result:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)

@customers_bp.route("/<customer_id>", methods=["PUT", "PATCH"])
def update_customer(customer_id):
    json_data = request.get_json()
    try:
        data = schema.load(json_data, partial=True)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    updated = CustomerService.update(customer_id, data)
    if not updated:
        return jsonify({"error": "not found"}), 404
    return jsonify(updated)

@customers_bp.route("/", methods=["GET"])
def list_customers():
    return jsonify(CustomerService.list_all())
