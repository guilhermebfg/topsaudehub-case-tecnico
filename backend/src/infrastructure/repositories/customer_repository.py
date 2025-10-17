from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session

from backend.src.application.dtos.customer import CustomerQuery
from backend.src.application.dtos.page import Page
from backend.src.exceptions import NotFoundException
from backend.src.infrastructure.models.customer import CustomerModel
from backend.src.infrastructure.repositories.base_repository import \
    BaseRepository


class CustomerRepository(BaseRepository[CustomerModel]):
    def __init__(self, session: Session):
        super().__init__(session, CustomerModel)

    def get(self, customer_id: int) -> CustomerModel:
        stmt = select(CustomerModel).where(CustomerModel.id == customer_id)
        customer = self.session.execute(stmt).scalars().one_or_none()

        if not customer:
            raise NotFoundException("Customer", customer_id)

        return customer

    def list(self, q: CustomerQuery,
             logic: str = "and") -> Page[CustomerModel]:
        stmt = select(CustomerModel)

        expressions = []

        # Apply filters
        if q.id:
            expressions.append(CustomerModel.id == q.id)
        if q.name:
            expressions.append(CustomerModel.name.ilike(f"%{q.name}%"))
        if q.email:
            expressions.append(CustomerModel.email.ilike(f"%{q.email}%"))
        if q.document:
            expressions.append(CustomerModel.document.ilike(f"%{q.document}%"))
        if q.created_min:
            expressions.append(CustomerModel.created_at >= q.created_min)

        if len(expressions) > 0:
            if logic == "and":
                stmt = stmt.where(and_(*expressions))
            else:
                stmt = stmt.where(or_(*expressions))

        total = self.session.scalar(
            select(func.count()).select_from(stmt.subquery())) or 0

        stmt = stmt.offset(q.first).limit(q.rows)

        if q.sort_order != 0:
            stmt = self._apply_sorting(stmt, q.sort_field, q.sort_order)

        customers = self.session.scalars(stmt).all()

        return Page(items=customers, total=total)

    def add(self, customer: CustomerModel) -> CustomerModel:
        self.session.add(customer)

        return customer

    def edit(self, customer: CustomerModel) -> CustomerModel:
        existing = self.get(customer.id)
        existing.name = customer.name
        existing.email = customer.email
        existing.document = customer.document

        return existing
