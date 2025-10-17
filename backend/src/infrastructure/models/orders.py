import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, DateTime, ForeignKey, event, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Numeric, Enum

from backend.src.infrastructure.models.base import Base


class OrderStatus(enum.Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default="0.00",
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="orderstatus"),
        nullable=False,
        default=OrderStatus.CREATED,
        server_default="CREATED",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    customer = relationship("CustomerModel", back_populates="orders")

    items = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def recalc_total(self):
        self.total_amount = sum((item.line_total or Decimal("0.00")) for item in self.items)


@event.listens_for(OrderModel.items, "append")
def _on_item_append(order: OrderModel, item, initiator):
    item._recalc_line()
    order.recalc_total()


@event.listens_for(OrderModel.items, "remove")
def _on_item_remove(order: OrderModel, item, initiator):
    order.recalc_total()
