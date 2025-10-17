from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, selectinload

from backend.src.application.dtos.order import OrderQuery
from backend.src.application.dtos.page import Page
from backend.src.exceptions import NotFoundException
from backend.src.infrastructure.models import OrderItemModel, CustomerModel
from backend.src.infrastructure.models.orders import OrderModel
from backend.src.infrastructure.repositories.base_repository import \
    BaseRepository


class OrderRepository(BaseRepository[OrderModel]):
    def __init__(self, session: Session):
        super().__init__(session, OrderModel)

    def get(self, order_id: int) -> OrderModel:
        stmt = (select(OrderModel)
                .options(
            selectinload(OrderModel.items),
            selectinload(OrderModel.customer)
        )
                .where(OrderModel.id == order_id))

        order = self.session.execute(stmt).scalars().one_or_none()

        if not order:
            raise NotFoundException("Order", order_id)

        return order

    def list(self, q: OrderQuery) -> Page[OrderModel]:
        stmt = (select(OrderModel)
                .options(selectinload(OrderModel.items),
                         selectinload(OrderModel.customer))
                )

        # Apply filters
        if q.id:
            stmt = stmt.where(OrderModel.id == q.id)
        if q.customer and q.customer.strip():
            customer = f"%{q.customer.strip()}%"
            stmt = stmt.where(OrderModel.customer.has(or_(
                CustomerModel.name.ilike(customer),
                CustomerModel.email.ilike(customer),
                CustomerModel.document.ilike(customer),
            )))
        if q.total_amount:
            stmt = stmt.where(OrderModel.total_amount >= q.total_amount)
        if q.status:
            stmt = stmt.where(OrderModel.status == q.status)
        if q.created_min:
            stmt = stmt.where(OrderModel.created_at >= q.created_min)

        total = self.session.scalar(
            select(func.count()).select_from(stmt.subquery())
        ) or 0

        stmt = stmt.offset(q.first).limit(q.rows)

        # Apply sorting using the base repository method
        if q.sort_order != 0:
            stmt = self._apply_sorting(stmt, q.sort_field, q.sort_order)

        orders = self.session.scalars(stmt).all()

        return Page(items=orders, total=total)

    def add(self, order: OrderModel) -> OrderModel:
        self.session.add(order)

        return order

    def edit(self, order: OrderModel) -> OrderModel:
        existing = self.get(order.id)

        existing.customer_id = order.customer_id
        existing.status = order.status

        existing_by_id = {i.id: i for i in existing.items if i.id is not None}
        seen_ids: set[int] = set()

        for inc in order.items:
            if inc.id and inc.id in existing_by_id:
                db_item = existing_by_id[inc.id]
                db_item.product_id = inc.product_id
                db_item.quantity = inc.quantity
                db_item.unit_price = inc.unit_price
                seen_ids.add(inc.id)
            else:
                new_item = OrderItemModel(
                    order_id=existing.id,
                    product_id=inc.product_id,
                    quantity=inc.quantity,
                    unit_price=inc.unit_price,
                )
                existing.items.append(new_item)

        for db_item in list(existing.items):
            if (db_item.id is not None and db_item.id not in seen_ids and
                    db_item.id in existing_by_id):
                existing.items.remove(db_item)

        existing.recalc_total()

        return existing
