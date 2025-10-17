import os, uuid, pytest, importlib
from datetime import datetime
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from backend.src.infrastructure.models.product import ProductModel
from backend.src.infrastructure.models.customer import CustomerModel
from backend.src.infrastructure.models.orders import OrderModel, OrderStatus
from backend.src.infrastructure.models.order_items import OrderItemModel


# 1) preparar um DB SQLite **antes de importar o app**
@pytest.fixture(scope="function")
def sqlite_url(tmp_path):
    db_path = tmp_path / f"test_{uuid.uuid4().hex}.db"
    url = f"sqlite:///{db_path}"
    # garantir que qualquer import que leia DATABASE_URL veja o SQLite
    os.environ["DATABASE_URL"] = url
    return url


@pytest.fixture(scope="function")
def engine(sqlite_url):
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, _):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON;")
        cur.close()

    # 2) criar as tabelas no engine de teste
    from backend.src.infrastructure.models import Base
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


# 3) sessão com **SAVEPOINT** (permite commits dentro do service)
@pytest.fixture(scope="function")
def test_session(engine) -> Generator[Session, None, None]:
    # conexão dedicada e transação raiz por teste
    connection = engine.connect()
    outer = connection.begin()

    SessionTesting = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session = SessionTesting()

    # transação aninhada (SAVEPOINT) – commits internos não conflitam
    nested = session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, transaction):
        nonlocal nested
        # quando um nested termina e o pai não é nested, reabre o SAVEPOINT
        if transaction.nested and not transaction._parent.nested:
            nested = sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        outer.rollback()   # descarta tudo do teste
        connection.close()


# 4) TestClient usando **uma NOVA Session por request**,
#    mas ligada ao MESMO connection do test_session (enxerga as fixtures)
@pytest.fixture(scope="function")
def client(engine, test_session):
    # MONKEYPATCH no módulo de DB para usar nosso engine
    import backend.src.infrastructure.database as dbmod
    dbmod.engine = engine

    # (recarregar main se ele cria coisas no import)
    import backend.src.main as mainmod
    importlib.reload(mainmod)
    app = mainmod.app

    def override_get_db():
        # cria uma Session nova por request, ligada ao MESMO connection do test_session
        SessionForRequest = sessionmaker(
            bind=test_session.bind,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        db = SessionForRequest()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[dbmod.get_db] = override_get_db

    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# -------------------------------
# Fixtures de dados (usam flush p/ gerar IDs)
# -------------------------------

@pytest.fixture(scope="function")
def sample_product(test_session) -> ProductModel:
    product = ProductModel(
        name="Test Product",
        sku="TES-001",
        price=99.99,
        stock_qty=10,
        is_active=True,
        created_at=datetime.now(),
    )
    test_session.add(product)
    test_session.flush()
    test_session.refresh(product)
    return product


@pytest.fixture(scope="function")
def sample_customer(test_session) -> CustomerModel:
    customer = CustomerModel(
        name="John Doe",
        email="john.doe@example.com",
        document="12345678900",
        created_at=datetime.now(),
    )
    test_session.add(customer)
    test_session.flush()
    test_session.refresh(customer)
    return customer


@pytest.fixture(scope="function")
def multiple_products(test_session) -> list[ProductModel]:
    products = []
    for i in range(15):
        product = ProductModel(
            name=f"Product {i}",
            sku=f"SKU-{i:03d}",
            price=10.0 + i,
            stock_qty=i * 10,
            is_active=i % 2 == 0,
            created_at=datetime.now(),
        )
        test_session.add(product)
        products.append(product)
    test_session.flush()
    return products


@pytest.fixture(scope="function")
def sample_order(test_session, sample_customer, multiple_products) -> OrderModel:
    order = OrderModel(
        customer_id=sample_customer.id,
        total_amount=199.98,
        status=OrderStatus.CREATED,
        created_at=datetime.now(),
    )
    test_session.add(order)
    test_session.flush()

    products = [x for x in multiple_products if x.is_active and x.stock_qty >= 2]
    for product in products:
        order_item = OrderItemModel(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            unit_price=99.99,
            line_total=199.98,
        )
        test_session.add(order_item)
    test_session.flush()
    test_session.refresh(order)
    return order


@pytest.fixture(scope="function")
def multiple_orders(test_session, sample_customer, sample_product) -> list[OrderModel]:
    orders = []
    for i in range(10):
        order = OrderModel(
            customer_id=sample_customer.id,
            total_amount=199.98,
            status=OrderStatus.CREATED,
            created_at=datetime.now(),
        )
        test_session.add(order)
        test_session.flush()
        test_session.refresh(order)

        order_item = OrderItemModel(
            order_id=order.id,
            product_id=sample_product.id,
            quantity=2,
            unit_price=99.99,
            line_total=199.98,
        )
        test_session.add(order_item)
        test_session.flush()
        test_session.refresh(order)
        orders.append(order)
    return orders


@pytest.fixture(scope="function")
def multiple_customers(test_session) -> list[CustomerModel]:
    customers = []
    for i in range(12):
        customer = CustomerModel(
            name=f"Customer {chr(i + 97)}",
            email=f"customer{i + 1}@example.com",
            document=f"000000000{(i + 20):02d}",
            created_at=datetime.now(),
        )
        test_session.add(customer)
        customers.append(customer)
    test_session.flush()
    return customers
