from marshmallow import Schema, fields

class ProductSchema(Schema):
    product_id = fields.Str(required=True)
    product_name = fields.Str(required=True)
    supplier_id = fields.Str()
    category = fields.Str()
    unit_price = fields.Float()
    units_in_stock = fields.Int()
