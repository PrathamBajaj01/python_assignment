# models/order.py
import os
import datetime
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, ListAttribute, MapAttribute,
    NumberAttribute, UTCDateTimeAttribute
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from ..config import Config

DEFAULT_TABLE = os.environ.get("ORDERS_TABLE", "Orders")
DEFAULT_REGION = os.environ.get("AWS_REGION", getattr(Config, "AWS_REGION", "us-east-1"))
DDB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT", getattr(Config, "DYNAMODB_ENDPOINT", None))


class OrderItem(MapAttribute):
    product_id = UnicodeAttribute()
    unit_price = NumberAttribute(null=True)
    quantity = NumberAttribute()


class CustomerIdIndex(GlobalSecondaryIndex):
    """
    Global secondary index to query orders by customer_id.
    Index name matches the CloudFormation / serverless.yml GSI name: customerId-index
    """
    class Meta:
        index_name = "customerId-index"
        projection = AllProjection()
        # read_capacity_units / write_capacity_units are optional when using PAY_PER_REQUEST
    customer_id = UnicodeAttribute(hash_key=True)


class OrderModel(Model):
    class Meta:
        table_name = DEFAULT_TABLE
        region = DEFAULT_REGION
        if DDB_ENDPOINT:
            host = DDB_ENDPOINT

    order_id = UnicodeAttribute(hash_key=True)
    customer_id = UnicodeAttribute(null=False)
    # attach the index so you can do OrderModel.customer_index.query(customer_id)
    customer_index = CustomerIdIndex()

    order_date = UTCDateTimeAttribute(default=datetime.datetime.utcnow)
    shipped_date = UTCDateTimeAttribute(null=True)
    ship_via = UnicodeAttribute(null=True)
    items = ListAttribute(of=OrderItem, null=True)
