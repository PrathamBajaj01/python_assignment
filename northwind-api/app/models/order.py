import os
import datetime
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UTCDateTimeAttribute
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from app.config import Config


class OrderItem(MapAttribute):
    product_id = UnicodeAttribute()
    unit_price = NumberAttribute(null=True)
    quantity = NumberAttribute()


class CustomerIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "customerId-index"
        projection = AllProjection()
    customer_id = UnicodeAttribute(hash_key=True)


class OrderModel(Model):
    class Meta:
        table_name = os.environ.get("ORDERS_TABLE", "Orders")
        region = Config.AWS_REGION
        if Config.DYNAMODB_ENDPOINT:
            host = Config.DYNAMODB_ENDPOINT

    order_id = UnicodeAttribute(hash_key=True)
    customer_id = UnicodeAttribute(null=False)
    customer_index = CustomerIdIndex()
    order_date = UTCDateTimeAttribute(default=datetime.datetime.utcnow)
    shipped_date = UTCDateTimeAttribute(null=True)
    ship_via = UnicodeAttribute(null=True)
    items = ListAttribute(of=OrderItem)
