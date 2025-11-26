from app.models.customer import CustomerModel
import os

print("CustomerModel.Meta.table_name =", CustomerModel.Meta.table_name)
print("CustomerModel.Meta.host =", getattr(CustomerModel.Meta, "host", None))
print("Env DYNAMODB_ENDPOINT =", os.getenv("DYNAMODB_ENDPOINT"))
print("Env AWS_REGION =", os.getenv("AWS_REGION"))
