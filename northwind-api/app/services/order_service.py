from typing import Dict, List, Optional
from app.models.order import OrderModel, OrderItem


def serialize(obj):
    if hasattr(obj, "attribute_values"):
        return serialize(obj.attribute_values)
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(v) for v in obj]
    return obj


class OrderService:
    @staticmethod
    def create(data: Dict) -> Dict:
        order = OrderModel(
            order_id=data["order_id"],
            customer_id=data["customer_id"],
            items=[
                OrderItem(
                    product_id=i["product_id"],
                    quantity=i["quantity"],
                    unit_price=i.get("unit_price")
                )
                for i in data["items"]
            ]
        )

        if "ship_via" in data:
            order.ship_via = data["ship_via"]
        if "shipped_date" in data:
            order.shipped_date = data["shipped_date"]

        order.save()
        return serialize(order.attribute_values)

    @staticmethod
    def get(order_id: str) -> Optional[Dict]:
        try:
            order = OrderModel.get(order_id)
            return serialize(order.attribute_values)
        except OrderModel.DoesNotExist:
            return None

    @staticmethod
    def update(order_id: str, data: Dict) -> Optional[Dict]:
        try:
            order = OrderModel.get(order_id)
        except OrderModel.DoesNotExist:
            return None

        for key in ("ship_via", "shipped_date"):
            if key in data:
                setattr(order, key, data[key])

        if "items" in data:
            order.items = [
                OrderItem(
                    product_id=i["product_id"],
                    quantity=i["quantity"],
                    unit_price=i.get("unit_price")
                )
                for i in data["items"]
            ]

        order.save()
        return serialize(order.attribute_values)

    @staticmethod
    def order_history(customer_id: str) -> List[Dict]:
        return [
            serialize(order.attribute_values)
            for order in OrderModel.customer_index.query(customer_id)
        ]
