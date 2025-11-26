# app/services/order_service.py
"""
Order service layer.

Provides OrderService with:
 - order_history(customer_id) -> list[dict]
 - get(order_id) -> dict | None
 - create(data) -> dict
 - update(order_id, data) -> dict

The implementation uses PynamoDB OrderModel and ensures returned objects
are plain Python types (JSON serializable).
"""
from typing import Any, Dict, List, Optional
from app.models.order import OrderModel


def _serialize(obj: Any) -> Any:
    """Recursively convert model instances / objects to JSON-serializable types."""
    # PynamoDB model instance -> attribute_values
    if hasattr(obj, "attribute_values"):
        return _serialize(obj.attribute_values)

    # dict -> recurse
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}

    # list/tuple -> recurse
    if isinstance(obj, (list, tuple)):
        return [_serialize(v) for v in obj]

    # objects with __dict__ (e.g. small custom objects) -> public attrs
    if hasattr(obj, "__dict__"):
        return {k: _serialize(v) for k, v in obj.__dict__.items() if not k.startswith("_")}

    # primitive -> return as-is
    return obj


class OrderService:
    @staticmethod
    def order_history(customer_id: str) -> List[Dict]:
        """
        Return a list of orders for the given customer_id, each as a plain dict.
        Adjust the query/scan to match your OrderModel key/index design.
        """
        results: List[Dict] = []
        # Prefer query if you have customer_id as a key or a GSI; fallback to scan
        try:
            # If OrderModel has a query method keyed on customer_id, replace this with it.
            # e.g.: for order in OrderModel.query(customer_id):
            for order in OrderModel.scan(OrderModel.customer_id == customer_id):
                # attribute_values is a dict but may contain nested Pynamo objects
                base = order.attribute_values if hasattr(order, "attribute_values") else {}
                base = _serialize(base)

                # If your model stores 'items' separately as attributes or objects, ensure we serialize them.
                if hasattr(order, "items"):
                    base["items"] = _serialize(getattr(order, "items"))

                results.append(base)
        except Exception:
            # Let the caller handle/log exceptions; re-raise for visibility during dev
            raise
        return results

    @staticmethod
    def get(order_id: str) -> Optional[Dict]:
        """Return a single order by id as a dict, or None if not found."""
        try:
            o = OrderModel.get(order_id)
            return _serialize(o.attribute_values)
        except OrderModel.DoesNotExist:
            return None

    @staticmethod
    def create(data: Dict) -> Dict:
        """Create order from a dict and return stored representation."""
        # Map incoming data to model fields. Adjust names as per your OrderModel.
        order = OrderModel(
            order_id=data.get("order_id"),
            customer_id=data.get("customer_id"),
        )
        # If your model defines attributes like items, set them:
        if "items" in data:
            setattr(order, "items", data["items"])
        # set other attributes if present
        for k, v in data.items():
            if k in ("order_id", "customer_id", "items"):
                continue
            try:
                setattr(order, k, v)
            except Exception:
                # skip unknown/readonly attrs
                pass

        order.save()
        return _serialize(order.attribute_values)

    @staticmethod
    def update(order_id: str, data: Dict) -> Optional[Dict]:
        """Update an existing order. Returns updated dict or None if not found."""
        try:
            order = OrderModel.get(order_id)
        except OrderModel.DoesNotExist:
            return None

        # apply updates (simple approach)
        for k, v in data.items():
            try:
                setattr(order, k, v)
            except Exception:
                pass
        order.save()
        return _serialize(order.attribute_values)
