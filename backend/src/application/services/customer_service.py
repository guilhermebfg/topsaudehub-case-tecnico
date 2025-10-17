import urllib.parse
from datetime import datetime

from backend.src.application.dtos.customer import (CustomerGet,
                                                   CustomerCreate,
                                                   CustomerEdit, CustomerQuery)
from backend.src.application.dtos.page import Page
from backend.src.exceptions import DuplicateEntryException
from backend.src.infrastructure.models import CustomerModel
from backend.src.infrastructure.repositories.customer_repository import \
    CustomerRepository


class CustomerService:
    def __init__(self, session, customer: CustomerRepository):
        self.session = session
        self.customer = customer

    def get(self, customer_id: int) -> CustomerGet:
        customer = self.customer.get(customer_id)
        customer = CustomerGet.model_validate(customer)
        return customer

    def list(self, q: CustomerQuery) -> Page[CustomerGet]:
        if (q.email is not None) and (q.email != ""):
            q.email = urllib.parse.unquote(q.email)

        data = self.customer.list(q)
        items = [CustomerGet.model_validate(customer) for customer in
                 data.items]

        return Page(items=items, total=data.total)

    def check_dupes(self, data: CustomerCreate):
        query = CustomerQuery(name=data.name, email=data.email,
                              document=data.document)

        dupe = self.customer.list(query, "or")

        return dupe.total > 0

    def add(self, data: CustomerCreate) -> CustomerGet:
        try:
            with self.session.begin():
                if self.check_dupes(data):
                    raise DuplicateEntryException("Customer")

                customer = CustomerModel(name=data.name, email=data.email,
                                         document=data.document,
                                         created_at=datetime.now())
                customer = self.customer.add(customer)

                self.session.flush()

            self.session.refresh(customer)
            return CustomerGet.model_validate(customer)
        except Exception as e:
            self.session.rollback()
            raise e

    def edit(self, data: CustomerEdit) -> CustomerGet:
        try:
            with self.session.begin():
                if self.check_dupes(data):
                    raise DuplicateEntryException("Customer")

                customer = CustomerModel(id=data.id, name=data.name,
                                         email=data.email,
                                         document=data.document)
                customer = self.customer.edit(customer)

                self.session.flush()
            self.session.refresh(customer)
            return CustomerGet.model_validate(customer)
        except Exception as e:
            self.session.rollback()
            raise e
