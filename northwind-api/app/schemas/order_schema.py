from marshmallow import Schema, fields, validate

class OrderItemSchema(Schema):
    product_id = fields.Str(required=True)
    unit_price = fields.Float()
    quantity = fields.Int(required=True, validate=validate.Range(min=1))

class OrderSchema(Schema):
    order_id = fields.Str(required=True)
    customer_id = fields.Str(required=True)
    order_date = fields.DateTime()
    shipped_date = fields.DateTime(allow_none=True)
    items = fields.List(fields.Nested(OrderItemSchema), required=True)
    ship_via = fields.Str()
