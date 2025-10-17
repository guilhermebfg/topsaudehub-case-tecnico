from decimal import Decimal
from sqlalchemy import Integer, ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Numeric

from backend.src.infrastructure.models.base import Base


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    order = relationship("OrderModel", back_populates="items")
    product = relationship("ProductModel", back_populates="items")

    def _recalc_line(self) -> None:
        q = Decimal(self.quantity or 0)
        p = self.unit_price if isinstance(self.unit_price, Decimal) else Decimal(self.unit_price or 0)
        self.line_total = (q * p).quantize(Decimal("0.01"))
        if self.order is not None:
            self.order.recalc_total()


@event.listens_for(OrderItemModel.quantity, "set", retval=False)
def _on_quantity_set(target: OrderItemModel, value, oldvalue, initiator):
    if value != oldvalue:
        target._recalc_line()


@event.listens_for(OrderItemModel.unit_price, "set", retval=False)
def _on_unit_price_set(target: OrderItemModel, value, oldvalue, initiator):
    if value != oldvalue:
        target._recalc_line()
