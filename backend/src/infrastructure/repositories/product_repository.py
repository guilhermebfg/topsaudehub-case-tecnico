from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.orm import Session

from backend.src.application.dtos.page import Page
from backend.src.application.dtos.product import ProductQuery
from backend.src.exceptions import NotFoundException
from backend.src.infrastructure.models.product import ProductModel
from backend.src.infrastructure.repositories.base_repository import \
    BaseRepository


class ProductRepository(BaseRepository[ProductModel]):
    def __init__(self, session: Session):
        super().__init__(session, ProductModel)

    def get(self, product_id: int) -> ProductModel:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        product = self.session.execute(stmt).scalars().one_or_none()

        if not product:
            raise NotFoundException("Product", product_id)

        return product

    def list(self, q: ProductQuery, logic = "and") -> Page[ProductModel]:
        stmt = select(ProductModel)

        expressions = []

        if q.id:
            expressions.append(ProductModel.id == q.id)
        if q.name:
            expressions.append(ProductModel.name.ilike(f"%{q.name}%"))
        if q.sku:
            expressions.append(ProductModel.sku.ilike(f"%{q.sku}%"))
        if q.price:
            expressions.append(ProductModel.price >= q.price)
        if q.stock_qty:
            expressions.append(ProductModel.stock_qty >= q.stock_qty)
        if q.is_active is not None:
            expressions.append(ProductModel.is_active == q.is_active)
        if q.created_min:
            expressions.append(ProductModel.created_at >= q.created_min)

        if len(expressions) > 0:
            if logic == "and":
                stmt = stmt.where(and_(*expressions))
            else:
                stmt = stmt.where(or_(*expressions))

        total = self.session.scalar(
            select(func.count()).select_from(stmt.subquery())
        ) or 0

        stmt = stmt.offset(q.first).limit(q.rows)

        # Apply sorting using the base repository method
        if q.sort_order != 0:
            stmt = self._apply_sorting(stmt, q.sort_field, q.sort_order)

        products = self.session.scalars(stmt).all()

        return Page(items=products, total=total)

    def add(self, product: ProductModel) -> ProductModel:
        self.session.add(product)

        return product

    def edit(self, data: ProductModel) -> ProductModel:
        stmt = select(ProductModel).where(ProductModel.id == data.id)
        product = self.session.execute(stmt).scalars().one_or_none()

        if not product:
            raise NotFoundException("Product", data.id)

        product.name = data.name
        product.sku = data.sku
        product.price = data.price
        product.stock_qty = data.stock_qty
        product.is_active = data.is_active

        return product

    def adjust_stock(self, deltas):
        for product_id, delta in deltas.items():
            stmt = (update(ProductModel)
                    .where(ProductModel.id == product_id)
                    .values(stock_qty=ProductModel.stock_qty - delta)
                    .returning(ProductModel))
            self.session.execute(stmt)
