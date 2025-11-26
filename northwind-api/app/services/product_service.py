from ..models.product import ProductModel
from pynamodb.exceptions import DoesNotExist

class ProductService:
    @staticmethod
    def create(data):
        p = ProductModel(**data)
        p.save()
        return p.attribute_values

    @staticmethod
    def get(product_id):
        try:
            p = ProductModel.get(product_id)
            return p.attribute_values
        except DoesNotExist:
            return None

    @staticmethod
    def update(product_id, patch):
        try:
            p = ProductModel.get(product_id)
            for k,v in patch.items():
                setattr(p, k, v)
            p.save()
            return p.attribute_values
        except DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return [r.attribute_values for r in ProductModel.scan()]
