from datetime import datetime

from backend.src.application.dtos.page import Page
from backend.src.application.dtos.product import ProductGet, ProductCreate, \
    ProductEdit, ProductQuery
from backend.src.exceptions import DuplicateEntryException
from backend.src.infrastructure.models import ProductModel
from backend.src.infrastructure.repositories.product_repository import \
    ProductRepository


class ProductService:
    def __init__(self, session, product: ProductRepository):
        self.session = session
        self.product = product

    def get(self, product_id: int) -> ProductGet:
        product = self.product.get(product_id)
        product = ProductGet.model_validate(product)
        return product

    def list(self, q: ProductQuery) -> Page[ProductGet]:
        data = self.product.list(q)
        items = [ProductGet.model_validate(product) for product in data.items]

        products = Page(
            items=items,
            total=data.total,
        )

        return products

    def check_dupes(self, data: ProductCreate):
        query = ProductQuery(name=data.name, sku=data.sku)
        dupe = self.product.list(query, "or")
        total = getattr(dupe, "total", dupe)
        return int(total) > 0

    def add(self, data: ProductCreate) -> ProductGet:
        try:
            with self.session.begin():
                if self.check_dupes(data):
                    raise DuplicateEntryException("Product")

                product = ProductModel(name=data.name, sku=data.sku,
                                       price=data.price,
                                       stock_qty=data.stock_qty,
                                       is_active=data.is_active,
                                       created_at=datetime.now())
                product = self.product.add(product)

                self.session.flush()
            self.session.refresh(product)
            return ProductGet.model_validate(product)
        except Exception as e:
            self.session.rollback()
            raise e

    def edit(self, data: ProductEdit) -> ProductGet:
        try:
            with self.session.begin():
                if self.check_dupes(data):
                    raise DuplicateEntryException("Product")

                product = ProductModel(
                    id=data.id,
                    name=data.name,
                    sku=data.sku,
                    price=data.price,
                    stock_qty=data.stock_qty,
                    is_active=data.is_active
                )

                product = self.product.edit(product)
                self.session.flush()

            self.session.refresh(product)
            return ProductGet.model_validate(product)
        except Exception as e:
            self.session.rollback()
            raise e
