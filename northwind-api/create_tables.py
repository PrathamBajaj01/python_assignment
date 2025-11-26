# create_tables.py
import os
import logging
from app.models.customer import CustomerModel
from app.models.product import ProductModel
from app.models.order import OrderModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("create_tables")

# Respect DYNAMODB_ENDPOINT if set
endpoint = os.getenv("DYNAMODB_ENDPOINT")
if endpoint:
    logger.info("Using DYNAMODB_ENDPOINT=%s", endpoint)
else:
    logger.info("No DYNAMODB_ENDPOINT set; using default boto/botocore behavior")

models = [CustomerModel, ProductModel, OrderModel]

for m in models:
    try:
        # PynamoDB provides exists() / create_table()
        if not m.exists():
            logger.info("Creating table: %s", m.Meta.table_name)
            # tune throughput for local testing
            m.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
            logger.info("Created table: %s", m.Meta.table_name)
        else:
            logger.info("Table already exists: %s", m.Meta.table_name)
    except Exception as e:
        logger.exception("Error creating table %s: %s", getattr(m.Meta, "table_name", m), e)
