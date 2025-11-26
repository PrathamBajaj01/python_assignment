# models/product.py
import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from ..config import Config

DEFAULT_TABLE = os.environ.get("PRODUCTS_TABLE", "Products")
DEFAULT_REGION = os.environ.get("AWS_REGION", getattr(Config, "AWS_REGION", "us-east-1"))
DDB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT", getattr(Config, "DYNAMODB_ENDPOINT", None))

class ProductModel(Model):
    class Meta:
        table_name = DEFAULT_TABLE
        region = DEFAULT_REGION
        if DDB_ENDPOINT:
            host = DDB_ENDPOINT

    product_id = UnicodeAttribute(hash_key=True)
    product_name = UnicodeAttribute(null=False)
    supplier_id = UnicodeAttribute(null=True)
    category = UnicodeAttribute(null=True)
    unit_price = NumberAttribute(null=True)
    units_in_stock = NumberAttribute(null=True)
