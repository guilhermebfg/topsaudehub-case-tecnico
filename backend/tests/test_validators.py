import pytest
from pydantic import ValidationError

from backend.src.application.dtos.customer import CustomerCreate
from backend.src.application.dtos.order import OrderCreate, OrderItemCreate
from backend.src.application.dtos.product import ProductCreate
from backend.src.infrastructure.models.orders import OrderStatus


class TestProductValidators:
    """Test Product DTO validators."""

    def test_product_create_valid(self):
        """Test creating a valid product."""
        product = ProductCreate(
            name="Test Product",
            sku="TES-001",
            price=99.99,
            stock_qty=10,
            is_active=True
        )
        assert product.name == "Test Product"
        assert product.sku == "TES-001"
        assert product.price == 99.99

    def test_product_name_too_short(self):
        """Test product name too short raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                name="AB",
                sku="TEST-001",
                price=99.99,
                stock_qty=10,
                is_active=True
            )
        assert "at least 3 characters" in str(exc_info.value).lower()

    def test_product_sku_empty(self):
        """Test empty SKU raises error."""
        with pytest.raises(ValidationError):
            ProductCreate(
                name="Test Product",
                sku="   ",
                price=99.99,
                stock_qty=10,
                is_active=True
            )

    def test_product_error_sku_uppercase(self):
        """Test SKU is converted to uppercase."""
        with pytest.raises(ValidationError) as exc_info:
            product = ProductCreate(
                name="Test Product",
                sku="test-001",
                price=99.99,
                stock_qty=10,
                is_active=True
            )
        assert "validation error" in str(exc_info.value).lower()

    def test_product_sku_invalid_characters(self):
        """Test SKU with invalid characters raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                name="Test Product",
                sku="TEST@001",
                price=99.99,
                stock_qty=10,
                is_active=True
            )
        assert "validation error" in str(exc_info.value).lower()

    def test_product_negative_price(self):
        """Test negative price raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                name="Test Product",
                sku="TEST-001",
                price=-10.0,
                stock_qty=10,
                is_active=True
            )
        assert "greater than 0" in str(exc_info.value).lower()

    def test_product_zero_price(self):
        """Test zero price raises error."""
        with pytest.raises(ValidationError):
            ProductCreate(
                name="Test Product",
                sku="TEST-001",
                price=0,
                stock_qty=10,
                is_active=True
            )

    def test_product_negative_stock(self):
        """Test negative stock raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                name="Test Product",
                sku="TEST-001",
                price=99.99,
                stock_qty=-5,
                is_active=True
            )
        assert "greater than or equal to 0" in str(exc_info.value).lower()

    def test_product_name_trimmed(self):
        """Test product name is trimmed."""
        product = ProductCreate(
            name="  Test Product  ",
            sku="TES-001",
            price=99.99,
            stock_qty=10,
            is_active=True
        )
        assert product.name == "Test Product"


class TestCustomerValidators:
    """Test Customer DTO validators."""

    def test_customer_create_valid(self):
        """Test creating a valid customer."""
        customer = CustomerCreate(
            name="John Doe",
            email="john@example.com",
            document="12345678901"
        )
        assert customer.name == "John Doe"
        assert customer.email == "john@example.com"
        assert customer.document == "12345678901"

    def test_customer_name_too_short(self):
        """Test customer name too short raises error."""
        with pytest.raises(ValidationError):
            CustomerCreate(
                name="AB",
                email="john@example.com",
                document="12345678901"
            )

    def test_customer_name_invalid_characters(self):
        """Test customer name with numbers raises error."""
        with pytest.raises(ValidationError) as exc_info:
            CustomerCreate(
                name="John123",
                email="john@example.com",
                document="12345678901"
            )
        assert "only letters" in str(exc_info.value).lower()

    def test_customer_name_trimmed(self):
        """Test customer name is trimmed."""
        customer = CustomerCreate(
            name="  John Doe  ",
            email="john@example.com",
            document="12345678901"
        )
        assert customer.name == "John Doe"

    def test_customer_invalid_email(self):
        """Test invalid email raises error."""
        with pytest.raises(ValidationError):
            CustomerCreate(
                name="John Doe",
                email="invalid-email",
                document="12345678901"
            )

    def test_customer_document_too_short(self):
        """Test document too short raises error."""
        with pytest.raises(ValidationError):
            CustomerCreate(
                name="John Doe",
                email="john@example.com",
                document="123456"
            )

    def test_customer_document_invalid_length(self):
        """Test document with invalid length raises error."""
        with pytest.raises(ValidationError) as exc_info:
            CustomerCreate(
                name="John Doe",
                email="john@example.com",
                document="123456789012"  # 12 digits, not 11 or 14
            )
        assert "11 digits" in str(exc_info.value) or "14 digits" in str(exc_info.value)

    def test_customer_document_all_same_digits(self):
        """Test document with all same digits raises error."""
        with pytest.raises(ValidationError) as exc_info:
            CustomerCreate(
                name="John Doe",
                email="john@example.com",
                document="11111111111"
            )
        assert "Invalid document" in str(exc_info.value)

    def test_customer_document_cleaned(self):
        """Test document is cleaned (only numbers)."""
        customer = CustomerCreate(
            name="John Doe",
            email="john@example.com",
            document="123.456.789-01"
        )
        assert customer.document == "12345678901"

    def test_customer_document_cnpj(self):
        """Test valid CNPJ document."""
        customer = CustomerCreate(
            name="Company Inc",
            email="contact@company.com",
            document="12345678000195"
        )
        assert customer.document == "12345678000195"


class TestOrderValidators:
    """Test Order DTO validators."""

    def test_order_create_valid(self):
        """Test creating a valid order."""
        order = OrderCreate(
            customer_id=1,
            items=[
                OrderItemCreate(
                    product_id=1,
                    quantity=1
                )
            ]
        )

        assert order.customer_id == 1
        assert order.items[0].product_id == 1
        assert order.items[0].quantity == 1

    def test_order_negative_customer_id(self):
        """Test negative customer_id raises error."""
        with pytest.raises(ValidationError):
            OrderCreate(
                customer_id=-1,
                items=[
                    OrderItemCreate(
                        product_id=1,
                        quantity=1
                    )
                ]
            )

    def test_order_zero_customer_id(self):
        """Test zero customer_id raises error."""
        with pytest.raises(ValidationError):
            OrderCreate(
                customer_id=0,
                items=[
                    OrderItemCreate(
                        product_id=1,
                        quantity=1
                    )
                ]
            )