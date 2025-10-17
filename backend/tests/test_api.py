import json

import pytest


class TestProductEndpoints:
    """Test product API endpoints."""

    def test_list_products(self, client, multiple_products):
        """Test listing products with pagination."""
        response = client.get("/api/products/?first=0&rows=10&sort_field=id&sort_order=1")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["cod_retorno"] == 200

        assert "items" in data["data"]
        assert "total" in data["data"]

        assert len(data["data"]["items"]) == 10
        assert data["data"]["total"] == 15

    def test_list_products_with_filter(self, client, multiple_products):
        """Test listing products with name filter."""
        response = client.get("/api/products/?first=0&rows=10&sort_field=id&sort_order=1&name=Product 1")

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert "data" in data
        assert "items" in data["data"]
        assert len(data["data"]["items"]) > 0

    def test_get_product_by_id(self, client, sample_product):
        """Test getting a specific product by ID."""
        response = client.get(f"/api/products/{sample_product.id}")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["mensagem"] is None
        assert data["cod_retorno"] == 200

        assert data["data"]["id"] == sample_product.id
        assert data["data"]["name"] == sample_product.name
        assert data["data"]["sku"] == sample_product.sku

    def test_get_product_not_found(self, client):
        """Test getting a non-existent product returns 404."""
        response = client.get("/api/products/999")

        assert response.status_code == 404
        data = response.json()
        assert data["cod_retorno"] == 404
        assert "not found" in data["mensagem"].lower()

    def test_create_product(self, client):
        """Test creating a new product."""
        new_product = {
            "name": "New API Product",
            "sku": "API-001",
            "price": 79.99,
            "stock_qty": 20,
            "is_active": True
        }
        response = client.post("/api/products/", json=new_product)

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert "mensagem" in data
        assert "data" in data
        assert "id" in data["data"]
        assert data["data"]["name"] == new_product["name"]
        assert data["data"]["sku"] == new_product["sku"]
        assert data["data"]["price"] == new_product["price"]

    def test_update_product(self, client, sample_product):
        """Test updating an existing product."""
        updated_data = {
            "id": sample_product.id,
            "name": "Updated Product Name",
            "sku": "NEW-001",
            "price": 129.99,
            "stock_qty": 15,
            "is_active": True
        }

        response = client.put("/api/products/", json=updated_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["name"] == "Updated Product Name"
        assert data["data"]["sku"] == "NEW-001"
        assert data["data"]["price"] == 129.99

    def test_list_products_invalid_sort_field(self, client, multiple_products):
        """Test listing products with invalid sort field returns 400."""
        response = client.get("/api/products/?first=0&rows=10&sort_field=invalid_field&sort_order=1")

        assert response.status_code == 400
        data = response.json()
        assert data["cod_retorno"] == 400


class TestCustomerEndpoints:
    """Test customer API endpoints."""

    def test_get_customer_by_id(self, client, sample_customer):
        """Test getting a specific customer by ID."""
        response = client.get(f"/api/customers/{sample_customer.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert data["data"]["id"] == sample_customer.id
        assert data["data"]["name"] == sample_customer.name
        assert data["data"]["email"] == sample_customer.email
        assert data["data"]["document"] == sample_customer.document

    def test_get_customer_not_found(self, client):
        """Test getting a non-existent customer returns 404."""
        response = client.get("/api/customers/999")

        assert response.status_code == 404
        data = response.json()
        assert data["cod_retorno"] == 404
        assert "not found" in data["mensagem"].lower()

    def test_list_customers(self, client, multiple_customers):
        """Test listing customers with pagination."""
        response = client.get("/api/customers/?first=0&rows=10&sort_field=id&sort_order=1")

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert len(data["data"]["items"]) == 10
        assert data["data"]["total"] == 12

    def test_create_customer(self, client):
        """Test creating a new customer."""
        new_customer = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "document": "12345678901"
        }

        response = client.post("/api/customers/", json=new_customer)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "id" in data["data"]
        assert data["data"]["name"] == new_customer["name"]
        assert data["data"]["email"] == new_customer["email"]
        assert data["data"]["document"] == new_customer["document"]

    def test_create_duplicate_customer(self, client):
        """Test creating a new customer."""
        new_customer = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "document": "12345678901"
        }

        response = client.post("/api/customers/", json=new_customer)
        dupe = client.post("/api/customers/", json=new_customer)

        assert dupe.status_code == 409
        data = dupe.json()
        assert data["cod_retorno"] == 409
        assert "already registered" in data["mensagem"]

    def test_update_customer(self, client, sample_customer):
        """Test updating an existing customer."""
        updated_data = {
            "id": sample_customer.id,
            "name": "Updated Customer Name",
            "email": "updated_customer@email.com",
            "document": "98765432101"
        }

        response = client.put("/api/customers/", json=updated_data)

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert "mensagem" in data
        assert data["data"]["name"] == "Updated Customer Name"
        assert data["data"]["email"] == "updated_customer@email.com"
        assert data["data"]["document"] == "98765432101"

    def test_list_customers_with_email_filter(self, client, multiple_customers):
        """Test listing customers with an email filter."""
        response = client.get("/api/customers/?first=0&rows=10&sort_field=id&sort_order=1&email=customer3")

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert len(data["data"]["items"]) == 1
        assert "customer3" in data["data"]["items"][0]["email"]

    def test_list_customers_with_name_filter(self, client, multiple_customers):
        """Test listing customers with a name filter."""
        response = client.get("/api/customers/?first=0&rows=10&sort_field=id&sort_order=1&name=Customer d")

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert len(data["data"]["items"]) == 1


class TestOrderEndpoints:
    """Test order API endpoints."""

    def test_list_orders(self, client, sample_order):
        """Test listing orders."""
        response = client.get("/api/orders/?first=0&rows=10&sort_field=id&sort_order=-1")

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert "data" in data
        assert len(data["data"]["items"]) >= 1
        assert data["data"]["total"] >= 1

        # Check order structure
        order = data["data"]["items"][0]
        assert "id" in order
        assert "customer" in order
        assert "items" in order
        assert "total_amount" in order
        assert "status" in order

    def test_get_order_by_id(self, client, sample_order):
        """Test listing orders."""
        response = client.get("/api/orders/1")

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert "mensagem" in data
        assert "data" in data
        # Check order structure
        order = data["data"]
        assert "id" in order
        assert "customer_id" in order
        assert "items" in order
        assert "total_amount" in order
        assert "status" in order

    def test_list_orders_with_sorting(self, client, sample_order):
        """Test listing orders with ascending sort."""
        response = client.get("/api/orders/?first=0&rows=10&sort_field=id&sort_order=1")

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200

    def test_create_order(self, client, sample_customer, sample_product):
        """Test creating a new order."""
        new_order = {
            "customer_id": 1,
            "total_amount": 199.98,
            "status": "CREATED",
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "unit_price": 99.99,
                    "line_total": 199.98
                }
            ]
        }
        response = client.post("/api/orders/", json=new_order)

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert "mensagem" in data
        assert "data" in data
        assert "id" in data["data"]
        assert data["data"]["customer_id"] == 1
        assert data["data"]["total_amount"] == 199.98
        assert data["data"]["status"] == "CREATED"
        assert len(data["data"]["items"]) == 1

    def test_update_order(self, client, sample_order, sample_product):
        """Test creating a new order."""
        new_order = {
            "id": sample_order.id,
            "customer_id": 1,
            "total_amount": 299.97,
            "items": [
                {
                    "id": 1,
                    "product_id": sample_product.id,
                    "quantity": 3,
                    "unit_price": 99.99,
                    "line_total": 299.97
                }
            ]
        }

        response = client.put("/api/orders/", json=new_order)

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert "mensagem" in data
        assert "data" in data
        assert "id" in data["data"]
        assert data["data"]["customer_id"] == 1
        assert float(data["data"]["total_amount"]) == 299.97
        assert data["data"]["status"] == "CREATED"
        assert len(data["data"]["items"]) == 1

    def test_charge_order(self, client, sample_order, sample_product):
        response = client.put(f"/api/orders/{sample_order.id}/charge")

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert "mensagem" in data
        assert "data" in data
        assert data["data"]["status"] == "PAID"

    def test_cancel_order(self, client, sample_order, sample_product):
        response = client.put(f"/api/orders/{sample_order.id}/cancel")

        assert response.status_code == 200
        data = response.json()
        assert data["cod_retorno"] == 200
        assert "mensagem" in data
        assert "data" in data
        assert data["data"]["status"] == "CANCELLED"


class TestErrorHandling:
    """Test error handling middleware."""

    def test_404_not_found_error(self, client):
        """Test 404 error is handled correctly."""
        response = client.get("/api/products/99999")

        assert response.status_code == 404
        data = response.json()
        assert data["cod_retorno"] == 404
        assert data["mensagem"] is not None
        assert data["data"] is None

    def test_invalid_sort_field_error(self, client, multiple_products):
        """Test invalid sort field error is handled correctly."""
        response = client.get("/api/products/?first=0&rows=10&sort_field=nonexistent&sort_order=1")

        assert response.status_code == 400
        data = response.json()
        assert data["cod_retorno"] == 400
        assert "Invalid sort field" in data["mensagem"]

    def test_business_rule_exception(self, client):
        """Test invalid sort field error is handled correctly."""
        response = client.get("/api/health/business-rule-exception")

        assert response.status_code == 422
        data = response.json()
        assert data["cod_retorno"] == 422
        assert "Product Invalid SKU" in data["mensagem"]

    def test_request_validation_exception(self, client):
        """Test invalid sort field error is handled correctly."""
        response = client.get("/api/health/request-validation-error")

        assert response.status_code == 422
        data = response.json()
        assert data["cod_retorno"] == 422
        assert "Validation error" in data["mensagem"]


    def test_duplicate_entry_exception(self, client):
        """Test invalid sort field error is handled correctly."""
        response = client.get("/api/health/duplicate-entry-error")

        assert response.status_code == 409
        data = response.json()
        assert data["cod_retorno"] == 409
        assert "already registered" in data["mensagem"]


class TestPaginationAndSorting:
    """Test pagination and sorting across endpoints."""

    def test_pagination_first_page(self, client, multiple_products):
        """Test getting first page of results."""
        response = client.get("/api/products/?first=0&rows=5&sort_field=id&sort_order=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 5

    def test_pagination_second_page(self, client, multiple_products):
        """Test getting second page of results."""
        response = client.get("/api/products/?first=5&rows=5&sort_field=id&sort_order=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 5

    def test_sorting_ascending(self, client, multiple_products):
        """Test sorting in ascending order."""
        response = client.get("/api/products/?first=0&rows=5&sort_field=price&sort_order=1")

        assert response.status_code == 200
        data = response.json()
        items = data["data"]["items"]
        prices = [item["price"] for item in items]
        assert prices == sorted(prices)

    def test_sorting_descending(self, client, multiple_products):
        """Test sorting in descending order."""
        response = client.get("/api/products/?first=0&rows=5&sort_field=price&sort_order=-1")

        assert response.status_code == 200
        data = response.json()
        items = data["data"]["items"]
        prices = [item["price"] for item in items]
        assert prices == sorted(prices, reverse=True)
