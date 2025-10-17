import os
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# permite rodar local com "python backend/seed.py"
import sys
ROOT = Path(__file__).resolve().parent  # .../backend
sys.path.insert(0, str(ROOT.parent))    # adiciona /app (ou raiz do repo)

from backend.src.infrastructure.models import (
    Base,
    ProductModel,
    CustomerModel,
    OrderModel,
    OrderItemModel,
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/interplayers_db",
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
faker = Faker("pt_BR")

def seed():
    session = SessionLocal()
    try:
        # limpa tabelas (ordem: itens -> pedidos -> produtos -> clientes)
        session.query(OrderItemModel).delete()
        session.query(OrderModel).delete()
        session.query(ProductModel).delete()
        session.query(CustomerModel).delete()
        session.commit()

        # ---- PRODUCTS ----
        products = []
        for _ in range(20):
            created = datetime.now(timezone.utc) - timedelta(days=faker.random_int(0, 90))
            p = ProductModel(
                name=faker.random_element([w for w in faker.words(100) if
                                           len(w) >= 3]).capitalize(),
                sku=faker.bothify(text="???-###").upper(),  # ABC-123
                price=Decimal(str(round(random.uniform(10, 5000), 2))),
                stock_qty=random.randint(0, 100),
                is_active=True,
                created_at=created,  # garante timestamp (evita True acidental)
            )
            products.append(p)
        session.add_all(products)
        session.commit()

        # ---- CUSTOMERS ----
        customers = []
        for _ in range(20):
            created = datetime.now(timezone.utc) - timedelta(days=faker.random_int(0, 90))
            c = CustomerModel(
                name=faker.first_name() + " " + faker.last_name(),
                email=faker.unique.email(),
                document=faker.cpf(),
                created_at=created,
            )
            customers.append(c)
        session.add_all(customers)
        session.commit()

        # ---- ORDERS + ORDER ITEMS ----
        for _ in range(20):
            cust = random.choice(customers)
            order_created = datetime.now(timezone.utc) - timedelta(days=faker.random_int(0, 30))
            order = OrderModel(customer_id=cust.id, status="CREATED", total_amount=Decimal("0.00"), created_at=order_created)
            session.add(order)
            session.flush()  # precisamos do order.id

            total = Decimal("0.00")
            for _ in range(random.randint(1, 4)):
                prod = random.choice(products)
                qty = random.randint(1, 5)
                unit = Decimal(str(prod.price))
                line_total = (unit * qty).quantize(Decimal("0.01"))
                total += line_total

                session.add(
                    OrderItemModel(
                        order_id=order.id,
                        product_id=prod.id,
                        unit_price=unit,
                        quantity=qty,
                        line_total=line_total,
                    )
                )

            order.total_amount = total.quantize(Decimal("0.01"))

        session.commit()
        print("✅ seed concluído")
    finally:
        session.close()

if __name__ == "__main__":
    seed()
