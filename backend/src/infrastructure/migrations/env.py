from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import os, sys
from pathlib import Path

HERE = Path(__file__).resolve()  # .../backend/src/infrastructure/migrations/env.py

backend_dir = None
for p in HERE.parents:
    if p.name.lower() == "backend" and (p / "src").exists():
        backend_dir = p
        break

if backend_dir is None:
    try:
        backend_dir = HERE.parents[3]
    except IndexError:
        raise RuntimeError(f"[alembic env] Não consegui resolver a pasta 'backend' a partir de {HERE}")

project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"[alembic env] backend_dir={backend_dir} | project_root={project_root}")

from backend.src.infrastructure.models import Base

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
