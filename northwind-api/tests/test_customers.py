from app.services.customer_service import CustomerService

def test_create_and_get_customer():
    payload = {"customer_id": "T100", "company_name":"TestCo"}
    created = CustomerService.create(payload)
    assert created["customer_id"] == "T100"
    fetched = CustomerService.get("T100")
    assert fetched["company_name"] == "TestCo"

def test_update_customer():
    payload = {"customer_id":"T200","company_name":"Old"}
    CustomerService.create(payload)
    updated = CustomerService.update("T200", {"company_name":"New"})
    assert updated["company_name"] == "New"
