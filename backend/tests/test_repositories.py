import pytest
from datetime import datetime, timedelta

from backend.src.application.dtos.customer import CustomerQuery
from backend.src.application.dtos.order import OrderQuery
from backend.src.application.dtos.product import ProductQuery
from backend.src.exceptions import NotFoundException, InvalidSortFieldException
from backend.src.infrastructure.models import OrderItemModel
from backend.src.infrastructure.models.customer import CustomerModel
from backend.src.infrastructure.models.product import ProductModel
from backend.src.infrastructure.repositories.customer_repository import CustomerRepository
from backend.src.infrastructure.repositories.order_repository import OrderRepository
from backend.src.infrastructure.repositories.product_repository import ProductRepository
from backend.src.infrastructure.models.orders import OrderModel, OrderStatus


class TestProductRepository:
    """Test ProductRepository."""

    def test_get_product_success(self, test_session, sample_product):
        """Test getting a product by id."""
        repo = ProductRepository(test_session)
        product = repo.get(sample_product.id)

        assert product.id == sample_product.id
        assert product.name == sample_product.name
        assert product.sku == sample_product.sku

    def test_get_product_not_found(self, test_session):
        """Test getting a non-existent product raises NotFoundException."""
        repo = ProductRepository(test_session)

        with pytest.raises(NotFoundException) as exc_info:
            repo.get(999)

        assert "Product with id 999 not found" in str(exc_info.value.detail)

    def test_list_products_with_pagination(self, test_session, multiple_products):
        """Test listing products with pagination."""
        repo = ProductRepository(test_session)
        query = ProductQuery(first=0, rows=10, sort_field="id", sort_order=1)

        result = repo.list(query)

        assert len(result.items) == 10
        assert result.total == 15

    def test_list_products_with_name_filter(self, test_session, multiple_products):
        """Test listing products with name filter."""
        repo = ProductRepository(test_session)
        query = ProductQuery(first=0, rows=10, sort_field="id", sort_order=1, name="Product 1")

        result = repo.list(query)

        assert len(result.items) > 0
        assert all("Product 1" in item.name for item in result.items)

    def test_list_products_with_id_filter(self, test_session, multiple_products):
        """Test listing products with id filter."""
        repo = ProductRepository(test_session)
        query = ProductQuery(first=0, rows=10, sort_field="id", sort_order=1, id=1)

        result = repo.list(query)

        assert len(result.items) > 0
        assert result.items[0].id == 1

    def test_list_products_with_sku_filter(self, test_session, multiple_products):
        """Test listing products with id filter."""
        repo = ProductRepository(test_session)
        query = ProductQuery(first=0, rows=10, sort_field="id", sort_order=1, sku="003")

        result = repo.list(query)

        assert len(result.items) > 0
        assert "003" in result.items[0].sku

    def test_list_products_with_price_filter(self, test_session, multiple_products):
        """Test listing products with id filter."""
        repo = ProductRepository(test_session)
        query = ProductQuery(first=0, rows=10, sort_field="id", sort_order=1, price=10)

        result = repo.list(query)

        assert len(result.items) == 10
        assert all(10 <= item.price for item in result.items)

    def test_list_products_with_stock_qty_filter(self, test_session, multiple_products):
        """Test listing products with id filter."""
        repo = ProductRepository(test_session)
        query = ProductQuery(first=0, rows=10, sort_field="id", sort_order=1, stock_qty=20)

        result = repo.list(query)

        assert len(result.items) == 10
        assert all(10 <= item.stock_qty for item in result.items)

    def test_list_products_with_is_active_filter(self, test_session, multiple_products):
        """Test listing products with id filter."""
        repo = ProductRepository(test_session)
        query = ProductQuery(first=0, rows=10, sort_field="id", sort_order=1, is_active=True)

        result = repo.list(query)

        assert all(item.is_active == True for item in result.items)

    def test_list_products_with_created_min_filter(self, test_session, multiple_products):
        """Test listing products with id filter."""
        repo = ProductRepository(test_session)
        date = datetime.now() - timedelta(days=1)
        query = ProductQuery(first=0, rows=10, sort_field="id", sort_order=1, created_min=date)

        result = repo.list(query)

        assert all(item.created_at >= date for item in result.items)

    def test_list_products_with_sorting_desc(self, test_session, multiple_products):
        """Test listing products with descending sort."""
        repo = ProductRepository(test_session)
        query = ProductQuery(first=0, rows=5, sort_field="price", sort_order=-1)

        result = repo.list(query)

        assert len(result.items) == 5
        # Check descending order
        prices = [item.price for item in result.items]
        assert prices == sorted(prices, reverse=True)

    def test_list_products_with_invalid_sort_field(self, test_session, multiple_products):
        """Test listing products with invalid sort field raises exception."""
        repo = ProductRepository(test_session)
        query = ProductQuery(first=0, rows=10, sort_field="invalid_field", sort_order=1)

        with pytest.raises(InvalidSortFieldException):
            repo.list(query)

    def test_add_product(self, test_session):
        """Test adding a new product."""
        repo = ProductRepository(test_session)
        new_product = ProductModel(
            name="New Product",
            sku="NEW-001",
            price=49.99,
            stock_qty=5,
            is_active=True,
            created_at=datetime.now()
        )

        result = repo.add(new_product)
        test_session.commit()
        assert result.id is not None
        assert result.name == "New Product"
        assert result.sku == "NEW-001"

    def test_edit_product(self, test_session, sample_product):
        """Test editing an existing product."""
        repo = ProductRepository(test_session)
        sample_product.name = "Updated Product"
        sample_product.price = 149.99

        result = repo.edit(sample_product)

        assert result.name == "Updated Product"
        assert float(result.price) == 149.99

    def test_edit_product_not_found(self, test_session):
        """Test editing a non-existent product raises NotFoundException."""
        repo = ProductRepository(test_session)
        fake_product = ProductModel(
            id=999,
            name="Fake",
            sku="FAKE",
            price=10.0,
            stock_qty=1,
            is_active=True
        )

        with pytest.raises(NotFoundException):
            repo.edit(fake_product)


class TestCustomerRepository:
    """Test CustomerRepository."""

    def test_get_customer_success(self, test_session, sample_customer):
        """Test getting a customer by id."""
        repo = CustomerRepository(test_session)
        customer = repo.get(sample_customer.id)

        assert customer.id == sample_customer.id
        assert customer.name == sample_customer.name
        assert customer.email == sample_customer.email

    def test_get_customer_not_found(self, test_session):
        """Test getting a non-existent customer raises NotFoundException."""
        repo = CustomerRepository(test_session)

        with pytest.raises(NotFoundException):
            repo.get(999)

    def test_list_customers_with_pagination(self, test_session, multiple_customers):
        """Test listing customers with pagination."""
        repo = CustomerRepository(test_session)
        query = CustomerQuery(first=0, rows=10, sort_field="id", sort_order=1)

        result = repo.list(query)

        assert len(result.items) == 10
        assert result.total == 12

    def test_list_customers_with_email_filter(self, test_session, multiple_customers):
        """Test listing customers with email filter."""
        repo = CustomerRepository(test_session)
        query = CustomerQuery(first=0, rows=10, sort_field="id", sort_order=1, email="customer5")

        result = repo.list(query)

        assert len(result.items) == 1
        assert "customer5" in result.items[0].email

    def test_list_customers_with_id_filter(self, test_session, multiple_customers):
        """Test listing customers with id filter."""
        repo = CustomerRepository(test_session)
        query = CustomerQuery(first=0, rows=10, sort_field="id", sort_order=1, id="5")

        result = repo.list(query)

        assert len(result.items) == 1
        assert result.items[0].id == 5

    def test_list_customers_with_document_filter(self, test_session, multiple_customers):
        """Test listing customers with id filter."""
        repo = CustomerRepository(test_session)
        query = CustomerQuery(first=0, rows=10, sort_field="id", sort_order=1, document="00000000021")

        result = repo.list(query)

        assert len(result.items) == 1
        assert result.items[0].document == "00000000021"

    def test_list_customers_with_creation_data_filter(self, test_session, multiple_customers):
        """Test listing customers with id filter."""
        repo = CustomerRepository(test_session)
        date = datetime.now() - timedelta(days=1)
        query = CustomerQuery(first=0, rows=10, sort_field="id", sort_order=1, created_min=date)

        result = repo.list(query)

        assert len(result.items) == 10
        assert result.items[0].created_at >= date

    def test_add_customer(self, test_session):
        """Test adding a new customer."""
        repo = CustomerRepository(test_session)
        new_customer = CustomerModel(
            name="Jane Smith",
            email="jane.smith@example.com",
            document="98765432100",
            created_at=datetime.now()
        )

        result = repo.add(new_customer)

        test_session.commit()
        assert result.id is not None
        assert result.name == "Jane Smith"
        assert result.email == "jane.smith@example.com"


class TestOrderRepository:
    """Test OrderRepository."""

    def test_get_order_success(self, test_session, sample_order):
        """Test getting an order by id with eager loading."""
        repo = OrderRepository(test_session)
        order = repo.get(sample_order.id)

        assert order.id == sample_order.id
        assert order.customer is not None
        assert order.items is not None
        assert len(order.items) > 0

    def test_get_order_not_found(self, test_session):
        """Test getting a non-existent order raises NotFoundException."""
        repo = OrderRepository(test_session)

        with pytest.raises(NotFoundException):
            repo.get(999)

    def test_list_orders_with_pagination(self, test_session, sample_order):
        """Test listing orders with pagination."""
        repo = OrderRepository(test_session)

        query = OrderQuery(first=0, rows=10, sort_field="id", sort_order=1)
        result = repo.list(query)

        assert len(result.items) >= 1
        assert result.total >= 1
        assert result.items[0].items is not None
        assert result.items[0].customer is not None

    def test_list_orders_with_id_filter(self, test_session, multiple_orders):
        """Test listing customers with id filter."""
        repo = OrderRepository(test_session)
        query = OrderQuery(first=0, rows=10, sort_field="id", sort_order=1, id=1)

        result = repo.list(query)

        assert len(result.items) == 1
        assert result.items[0].id == 1

    def test_list_orders_with_customer_name_filter(self, test_session, multiple_orders):
        """Test listing customers with id filter."""
        repo = OrderRepository(test_session)
        query = OrderQuery(first=0, rows=10, sort_field="id", sort_order=1, customer=multiple_orders[0].customer.name)

        result = repo.list(query)

        assert len(result.items) == 10

    def test_list_orders_with_customer_document_filter(self, test_session, multiple_orders):
        """Test listing customers with id filter."""
        repo = OrderRepository(test_session)
        query = OrderQuery(first=0, rows=10, sort_field="id", sort_order=1, customer=multiple_orders[0].customer.document)

        result = repo.list(query)

        assert len(result.items) == 10

    def test_list_orders_with_amount_filter(self, test_session, multiple_orders):
        """Test listing customers with id filter."""
        repo = OrderRepository(test_session)
        query = OrderQuery(first=0, rows=10, sort_field="id", sort_order=1, total_amount=multiple_orders[0].total_amount - 10)

        result = repo.list(query)

        assert len(result.items) == 10

    def test_list_orders_with_status_filter(self, test_session, multiple_orders):
        """Test listing customers with id filter."""
        repo = OrderRepository(test_session)
        query = OrderQuery(first=0, rows=10, sort_field="id", sort_order=1, status="CREATED")

        result = repo.list(query)

        assert len(result.items) == 10

    def test_list_orders_with_customer_email_filter(self, test_session, multiple_orders):
        """Test listing customers with id filter."""
        repo = OrderRepository(test_session)
        query = OrderQuery(first=0, rows=10, sort_field="id", sort_order=1, customer=multiple_orders[0].customer.email[:5])

        result = repo.list(query)

        assert len(result.items) == 10

    def test_list_orders_with_creation_date_filter(self, test_session, multiple_orders):
        """Test listing customers with id filter."""
        repo = OrderRepository(test_session)
        date = datetime.now() - timedelta(days=1)
        query = OrderQuery(first=0, rows=10, sort_field="id", sort_order=1, created_min=date)

        result = repo.list(query)

        assert len(result.items) == 10

    def test_add_order(self, test_session, sample_customer, sample_product):
        """Test adding a new order."""
        repo = OrderRepository(test_session)

        new_order = OrderModel(
            customer_id=sample_customer.id,
            status=OrderStatus.CREATED,
            created_at=datetime.now()
        )

        new_order.items.append(OrderItemModel(
            product_id=sample_product.id,
            quantity=1,
            unit_price=10.0
        ))

        new_order.recalc_total()

        result = repo.add(new_order)
        test_session.commit()

        assert result.id is not None
        assert result.customer_id == sample_customer.id
        assert float(result.total_amount) == 10.00

