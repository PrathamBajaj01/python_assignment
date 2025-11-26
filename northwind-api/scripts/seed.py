# scripts/seed.py
from app.services.customer_service import CustomerService
from app.services.product_service import ProductService
from app.services.order_service import OrderService

# customers
CustomerService.create({"customer_id":"C001","company_name":"ACME Corp","contact_name":"Alice"})
CustomerService.create({"customer_id":"C002","company_name":"Beta Ltd","contact_name":"Bob"})

# products
ProductService.create({"product_id":"P001","product_name":"Widget","unit_price":9.99,"units_in_stock":100})
ProductService.create({"product_id":"P002","product_name":"Gadget","unit_price":19.99,"units_in_stock":50})

# orders
OrderService.create({"order_id":"O001","customer_id":"C001","order_date":"2025-11-21","items":[{"product_id":"P001","quantity":2,"unit_price":9.99}]})
print("Seed complete")
