# tests/conftest.py
import os
import pytest
from moto import mock_dynamodb

@pytest.fixture(autouse=True, scope="session")
def dynamodb_server():
    
    mock = mock_dynamodb()
    mock.start()

   
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

    
    os.environ.pop("DYNAMODB_ENDPOINT", None)

 
    from app.models.customer import CustomerModel
    from app.models.product import ProductModel
    from app.models.order import OrderModel

   
    if getattr(CustomerModel.Meta, "host", None):
        CustomerModel.Meta.host = None
    if getattr(ProductModel.Meta, "host", None):
        ProductModel.Meta.host = None
    if getattr(OrderModel.Meta, "host", None):
        OrderModel.Meta.host = None

   
    CustomerModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    ProductModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    OrderModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    yield

    
    mock.stop()
