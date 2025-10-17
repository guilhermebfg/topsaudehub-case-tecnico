from datetime import datetime

from sqlalchemy.orm import Session

from backend.src.application.dtos.order import OrderGet, OrderCreate, \
    OrderEdit, OrderQuery
from backend.src.application.dtos.page import Page
from backend.src.exceptions import NotFoundException
from backend.src.infrastructure.models import OrderModel
from backend.src.infrastructure.models.order_items import OrderItemModel
from backend.src.infrastructure.models.orders import OrderStatus
from backend.src.infrastructure.repositories.order_repository import \
    OrderRepository
from backend.src.infrastructure.repositories.product_repository import \
    ProductRepository


def _deltas_from_diff(old, new):
    o, n = {}, {}
    for it in old:
        o[it.product.id] = o.get(it.product.id, 0) + it.quantity
    for it in new:
        n[it.product_id] = n.get(it.product_id, 0) + it.quantity
    keys = set(o) | set(n)
    return {k: n.get(k, 0) - o.get(k, 0) for k in keys if
            n.get(k, 0) != o.get(k, 0)}


def _deltas_from_items(new):
    d = {}
    for it in new:
        d[it.product_id] = it.quantity - d.get(it.product_id, 0)
    return d


class OrderService:
    def __init__(self, session: Session, order: OrderRepository,
                 product: ProductRepository):
        self.session = session
        self.order = order
        self.product = product

    def get(self, order_id: int) -> OrderGet:
        order = self.order.get(order_id)
        order = OrderGet.model_validate(order)
        return order

    def list(self, q: OrderQuery) -> Page[OrderGet]:
        data = self.order.list(q)
        items = [OrderGet.model_validate(order) for order in data.items]

        orders = Page(items=items, total=data.total, )

        return orders

    def add(self, data: OrderCreate) -> OrderGet:
        try:
            with self.session.begin():

                order = OrderModel(customer_id=data.customer_id,
                                   status=OrderStatus.CREATED,
                                   created_at=datetime.now())

                # Add order items
                for item_data in data.items:
                    product = self.product.get(item_data.product_id)

                    order_item = OrderItemModel(product_id=product.id,
                                                unit_price=product.price,
                                                quantity=item_data.quantity, )

                    order.items.append(order_item)

                order.recalc_total()
                order = self.order.add(order)

                deltas = _deltas_from_items(new=order.items)
                self.product.adjust_stock(deltas=deltas)

                self.session.flush()

            self.session.refresh(order)
            return OrderGet.model_validate(order)
        except Exception as e:
            self.session.rollback()
            raise e

    def edit(self, data: OrderEdit) -> OrderGet:
        try:
            with self.session.begin():
                existing = self.get(data.id)

                order = OrderModel(id=data.id, customer_id=data.customer_id,
                                   status=existing.status,
                                   created_at=existing.created_at)

                # Add order items
                for item_data in data.items:
                    order_item = (
                        OrderItemModel(id=item_data.id,
                                       order_id=data.id,
                                       product_id=item_data.product_id,
                                       unit_price=item_data.unit_price,
                                       quantity=item_data.quantity))

                    order.items.append(order_item)

                updated = self.order.edit(order)

                deltas = _deltas_from_diff(old=existing.items, new=order.items)
                self.product.adjust_stock(deltas=deltas)

                self.session.flush()

            self.session.refresh(updated)
            return OrderGet.model_validate(updated)
        except Exception as e:
            self.session.rollback()
            raise e

    def charge(self, order_id: int):
        try:
            with self.session.begin():
                order = self.order.get(order_id)

                if order.status != OrderStatus.CREATED:
                    raise NotFoundException(
                        f"Order {order_id} is not in the created state")

                order.status = OrderStatus.PAID
                order = self.order.edit(order)

                self.session.flush()

            self.session.refresh(order)
            return order
        except Exception as e:
            self.session.rollback()
            raise e

    def cancel(self, order_id: int):
        try:
            with self.session.begin():
                order = self.order.get(order_id)

                if order.status == OrderStatus.CANCELLED:
                    raise NotFoundException(
                        f"Order {order_id} is already cancelled")

                order.status = OrderStatus.CANCELLED
                order = self.order.edit(order)

                for item in order.items:
                    self.product.adjust_stock(
                        {item.product_id: -item.quantity})

                self.session.flush()
            self.session.refresh(order)
            return order
        except Exception as e:
            self.session.rollback()
            raise e
