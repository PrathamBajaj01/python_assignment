from app.models.customer import CustomerModel
from app.models.product import ProductModel
from app.models.order import OrderModel

CustomerModel(customer_id="C001", company_name="ACME Corp", contact_name="Alice").save()
ProductModel(product_id="P001", product_name="Widget", unit_price=9.99, units_in_stock=100).save()
OrderModel(order_id="O001", customer_id="C001", items=[{"product_id":"P001","unit_price":9.99,"quantity":2}]).save()
print("Seed done")
