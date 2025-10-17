from fastapi import Depends
from sqlalchemy.orm import Session

from backend.src.application.services.customer_service import CustomerService
from backend.src.application.services.order_service import OrderService
from backend.src.application.services.product_service import ProductService
from backend.src.infrastructure.database import get_db
from backend.src.infrastructure.repositories.customer_repository import \
    CustomerRepository
from backend.src.infrastructure.repositories.order_repository import \
    OrderRepository
from backend.src.infrastructure.repositories.product_repository import \
    ProductRepository


def get_product_service(session: Session = Depends(get_db)) -> ProductService:
    """Injecao de dependencia de servico de produto."""
    repository = ProductRepository(session)
    return ProductService(session, repository)


def get_customer_service(
        session: Session = Depends(get_db)) -> CustomerService:
    """Injecao de dependencia de servico de clientes."""
    repository = CustomerRepository(session)
    return CustomerService(session, repository)


def get_order_service(session: Session = Depends(get_db)) -> OrderService:
    """Injecao de dependencia de servico de pedidos."""
    order_repository = OrderRepository(session)
    product_repository = ProductRepository(session)
    return OrderService(session, order_repository, product_repository)
