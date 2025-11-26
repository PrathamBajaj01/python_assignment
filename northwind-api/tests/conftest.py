# tests/conftest.py
import os
import pytest
from moto import mock_dynamodb

@pytest.fixture(autouse=True, scope="session")
def dynamodb_server():
    """
    Start moto's mock_dynamodb for the whole test session, then import models and
    create tables. This ensures PynamoDB/boto clients are created after moto is active.
    """
    # 1) Start moto mock
    mock = mock_dynamodb()
    mock.start()

    # 2) Ensure boto/botocore have credentials (moto doesn't require real values)
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

    # 3) IMPORTANT: If your models set Meta.host from environment variable
    #    (e.g. DYNAMODB_ENDPOINT) make sure it's unset so models use moto.
    os.environ.pop("DYNAMODB_ENDPOINT", None)

    # 4) Now import the models (after moto is active)
    from app.models.customer import CustomerModel
    from app.models.product import ProductModel
    from app.models.order import OrderModel

    # If your models have Meta.host explicitly set to 'http://localhost:8000',
    # override it here so PynamoDB connects via moto (local mock).
    if getattr(CustomerModel.Meta, "host", None):
        CustomerModel.Meta.host = None
    if getattr(ProductModel.Meta, "host", None):
        ProductModel.Meta.host = None
    if getattr(OrderModel.Meta, "host", None):
        OrderModel.Meta.host = None

    # 5) Create tables
    CustomerModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    ProductModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    OrderModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    yield

    # 6) Teardown: stop moto
    mock.stop()
