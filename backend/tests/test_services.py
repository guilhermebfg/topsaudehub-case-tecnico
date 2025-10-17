from datetime import datetime
from unittest.mock import Mock, MagicMock

from sqlalchemy.orm import sessionmaker

from backend.src.application.dtos.customer import CustomerCreate, CustomerQuery
from backend.src.application.dtos.order import OrderQuery
from backend.src.application.dtos.page import Page
from backend.src.application.dtos.product import ProductQuery
from backend.src.application.services.customer_service import CustomerService
from backend.src.application.services.order_service import OrderService
from backend.src.application.services.product_service import ProductService
from backend.src.infrastructure.models.customer import CustomerModel
from backend.src.infrastructure.models.orders import OrderModel, OrderStatus
from backend.src.infrastructure.models.product import ProductModel


def _new_service_session(test_session):
    """Cria uma Session nova ligada ao MESMO connection do test_session."""
    SessionForSvc = sessionmaker(bind=test_session.bind, autoflush=False,
        autocommit=False, expire_on_commit=False, )
    return SessionForSvc()


class TestProductService:
    def test_get_product(self, test_session):
        svc_session = _new_service_session(test_session)

        mock_repo = Mock(spec=["get"])
        mock_product = ProductModel(id=1, name="Test Product", sku="TES-001",
            price=99.99, stock_qty=10, is_active=True,
            created_at=datetime.now(), )
        mock_repo.get.return_value = mock_product

        service = ProductService(svc_session, mock_repo)
        result = service.get(1)

        assert result.id == 1
        assert result.name == "Test Product"
        mock_repo.get.assert_called_once_with(1)

        svc_session.close()

    def test_list_products(self, test_session):
        svc_session = _new_service_session(test_session)

        mock_repo = Mock(spec=["list"])
        mock_products = [
            ProductModel(id=i, name=f"Product {i}", sku=f"SKU-00{i}",
                price=10.0 * i, stock_qty=i, is_active=True,
                created_at=datetime.now(), ) for i in range(1, 6)]
        mock_page = Page(items=mock_products, total=5)
        mock_repo.list.return_value = mock_page

        service = ProductService(svc_session, mock_repo)
        query = ProductQuery(first=0, rows=10, sort_field="id", sort_order=1)
        result = service.list(query)

        assert len(result.items) == 5
        assert result.total == 5
        assert all(hasattr(item, "name") for item in result.items)
        mock_repo.list.assert_called_once_with(query)

        svc_session.close()


class TestCustomerService:
    def test_get_customer(self, test_session):
        svc_session = _new_service_session(test_session)

        mock_repo = Mock(spec=["get"])
        mock_customer = CustomerModel(id=1, name="John Doe",
            email="john@example.com", document="12345678900",
            created_at=datetime.now(), )
        mock_repo.get.return_value = mock_customer

        service = CustomerService(svc_session, mock_repo)
        result = service.get(1)

        assert result.id == 1
        assert result.name == "John Doe"
        mock_repo.get.assert_called_once_with(1)

        svc_session.close()

    def test_list_customers(self, test_session):
        svc_session = _new_service_session(test_session)

        mock_repo = Mock(spec=["list"])
        mock_customers = [CustomerModel(id=i, name=f"Customer {chr(i + 97)}",
            email=f"customer{i}@example.com", document=f"{i:011d}",
            created_at=datetime.now(), ) for i in range(1, 6)]
        mock_page = Page(items=mock_customers, total=5)
        mock_repo.list.return_value = mock_page

        service = CustomerService(svc_session, mock_repo)
        query = CustomerQuery(first=0, rows=10, sort_field="id", sort_order=1)
        result = service.list(query)

        assert len(result.items) == 5
        assert result.total == 5
        mock_repo.list.assert_called_once_with(query)

        svc_session.close()

    def test_list_customers_with_url_encoded_email(self, test_session):
        svc_session = _new_service_session(test_session)

        mock_repo = Mock(spec=["list"])
        mock_customers = [
            CustomerModel(id=1, name="Test User", email="test@example.com",
                document="12345678900", created_at=datetime.now(), )]
        mock_page = Page(items=mock_customers, total=1)
        mock_repo.list.return_value = mock_page

        service = CustomerService(svc_session, mock_repo)
        query = CustomerQuery(first=0, rows=10, sort_field="id", sort_order=1,
            email="test%40example.com")
        result = service.list(query)

        assert query.email == "test@example.com"
        assert len(result.items) == 1
        mock_repo.list.assert_called_once()

        svc_session.close()

    def test_add_customer(self, test_session):
        svc_session = _new_service_session(test_session)

        def _add_side_effect(dto: CustomerCreate):
            entity = CustomerModel(name=dto.name, email=dto.email,
                document=dto.document, created_at=datetime.now(), )
            svc_session.add(entity)
            svc_session.flush()
            return entity

        mock_repo = Mock(spec=["add", "get", "list"])
        mock_repo.add.side_effect = _add_side_effect
        mock_repo.get.return_value = None
        mock_repo.list.return_value = Page(items=[], total=0)

        service = CustomerService(svc_session, mock_repo)
        dto = CustomerCreate(name="Jane Smith", email="jane@example.com",
            document="98765432100", )
        result = service.add(dto)

        assert result.id is not None
        assert result.name == "Jane Smith"
        assert result.email == "jane@example.com"
        mock_repo.add.assert_called_once()

        svc_session.close()


class TestOrderService:
    def test_get_order(self, test_session):
        svc_session = _new_service_session(test_session)

        mock_order_repo = Mock(spec=["get", "list"])
        mock_product_repo = Mock(spec=["get"])

        mock_customer = MagicMock(spec=CustomerModel)
        mock_customer.id = 1
        mock_customer.name = "Customer a"
        mock_customer.email = "customer1@example.com"
        mock_customer.document = f"{1:011d}"

        mock_order = MagicMock(spec=OrderModel)
        mock_order.id = 1
        mock_order.customer_id = 1
        mock_order.customer = mock_customer
        mock_order.total_amount = 199.98
        mock_order.status = OrderStatus.CREATED
        mock_order.created_at = datetime.now()
        mock_order.items = []

        mock_order_repo.get.return_value = mock_order

        service = OrderService(svc_session, mock_order_repo, mock_product_repo)
        result = service.get(1)

        assert result.id == 1
        mock_order_repo.get.assert_called_once_with(1)

        svc_session.close()

    def test_list_orders(self, test_session):
        svc_session = _new_service_session(test_session)

        mock_order_repo = Mock(spec=["list"])
        mock_product_repo = Mock(spec=["get"])

        mock_orders = []
        for i in range(1, 4):
            mock_customer = MagicMock(spec=CustomerModel)
            mock_customer.id = i
            mock_customer.name = f"Customer {chr(i + 97)}"
            mock_customer.email = f"customer{i}@example.com"
            mock_customer.document = f"{i:011d}"

            mock_order = MagicMock(spec=OrderModel)
            mock_order.id = i
            mock_order.customer_id = i
            mock_order.total_amount = 100.0 * i
            mock_order.status = OrderStatus.CREATED
            mock_order.created_at = datetime.now()
            mock_order.items = []
            mock_order.customer = mock_customer
            mock_orders.append(mock_order)

        mock_page = Page(items=mock_orders, total=3)
        mock_order_repo.list.return_value = mock_page

        service = OrderService(svc_session, mock_order_repo, mock_product_repo)
        query = OrderQuery(first=0, rows=10, sort_field="id", sort_order=-1)
        result = service.list(query)

        assert len(result.items) == 3
        assert result.total == 3
        called_query = mock_order_repo.list.call_args.args[0]
        assert called_query.first == 0
        assert called_query.rows == 10
        assert called_query.sort_field == "id"
        assert called_query.sort_order == -1

        svc_session.close()
