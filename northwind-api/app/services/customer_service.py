from ..models.customer import CustomerModel
from pynamodb.exceptions import DoesNotExist

class CustomerService:
    @staticmethod
    def create(data):
        c = CustomerModel(**data)
        c.save()
        return c.attribute_values

    @staticmethod
    def get(customer_id):
        try:
            c = CustomerModel.get(customer_id)
            return c.attribute_values
        except DoesNotExist:
            return None

    @staticmethod
    def update(customer_id, patch):
        try:
            c = CustomerModel.get(customer_id)
            for k,v in patch.items():
                setattr(c, k, v)
            c.save()
            return c.attribute_values
        except DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return [r.attribute_values for r in CustomerModel.scan()]
