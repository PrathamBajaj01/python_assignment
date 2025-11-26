# models/customer.py
import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
from ..config import Config  # keep if your package structure uses this

DEFAULT_TABLE = os.environ.get("CUSTOMERS_TABLE", "Customers")
DEFAULT_REGION = os.environ.get("AWS_REGION", getattr(Config, "AWS_REGION", "us-east-1"))
DDB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT", getattr(Config, "DYNAMODB_ENDPOINT", None))

class CustomerModel(Model):
    class Meta:
        table_name = DEFAULT_TABLE
        region = DEFAULT_REGION
        if DDB_ENDPOINT:
            host = DDB_ENDPOINT

    # attribute names are snake_case in code; DynamoDB attribute names will match these
    customer_id = UnicodeAttribute(hash_key=True)
    company_name = UnicodeAttribute(null=False)
    contact_name = UnicodeAttribute(null=True)
    contact_title = UnicodeAttribute(null=True)
    address = UnicodeAttribute(null=True)
    city = UnicodeAttribute(null=True)
    country = UnicodeAttribute(null=True)
    phone = UnicodeAttribute(null=True)
