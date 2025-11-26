from marshmallow import Schema, fields

class CustomerSchema(Schema):
    customer_id = fields.Str(required=True)
    company_name = fields.Str(required=True)
    contact_name = fields.Str()
    contact_title = fields.Str()
    address = fields.Str()
    city = fields.Str()
    country = fields.Str()
    phone = fields.Str()
