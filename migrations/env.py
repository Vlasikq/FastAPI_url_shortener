import sys
import os
# Добавляем корневую директорию проекта в PYTHONPATH, чтобы импортировать модули из src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from src.config import settings
from src.database.models import Base

# Настройка логирования согласно файлу конфигурации alembic.ini
fileConfig(context.config.config_file_name)

# Получаем объект конфигурации Alembic
config = context.config
# Переопределяем строку подключения к базе, беря значение из настроек
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
# Устанавливаем метаданные, на основе которых будет строиться автогенерация миграций
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, 
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
