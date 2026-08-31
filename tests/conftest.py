# module_26_fastapi/homework/tests/conftest.py

import asyncio
import pytest
import httpx
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from ..database import Base
import module_26_fastapi.homework.database as db_module
from ..main import app




TEST_URL = "sqlite+aiosqlite:///test_db.db"

test_engine = create_async_engine(TEST_URL, echo=False)
test_session = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

print(f"Зарегистрированные таблицы: {list(Base.metadata.tables.keys())}")
assert 'recepts' in Base.metadata.tables, "Таблица 'recepts' не зарегистрирована в Base!"


@pytest.fixture(scope="session")
def event_loop():
    """Создаёт event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_db():
    """Создаёт и удаляет таблицы БД для всех тестов"""
    async with test_engine.begin() as conn:
        print('===========================СОЗДАНИЕ===============================')
        await conn.run_sync(Base.metadata.create_all)
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Созданы таблицы: {tables}")

        # Проверяем наличие recepts
        assert 'recepts' in tables, "Таблица 'recepts' не была создана!"

    yield

    print("=== УДАЛЕНИЕ ТАБЛИЦ ===")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session(setup_db):
    """Создаёт тестовую сессию и ПОДМЕНЯЕТ глобальную"""
    # Сохраняем оригинальную сессию
    original_session = db_module.session

    # Создаём тестовую сессию БЕЗ begin()
    async with test_session() as sess:
        # ПОДМЕНЯЕМ ГЛОБАЛЬНУЮ СЕССИЮ
        db_module.session = sess

        yield sess

        # Восстанавливаем оригинальную сессию
        db_module.session = original_session


@pytest.fixture(scope="function")
async def client(db_session):
    """Создаёт HTTP клиент с подменой зависимости БД"""

    # Подменяем зависимость get_db на тестовую сессию
    async def override_get_db():
        yield db_session

    app.dependency_overrides[db_module.get_db] = override_get_db

    # Создаём клиент с ASGITransport для FastAPI
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    # Очищаем подмену после теста
    app.dependency_overrides.clear()

pytest_plugins = ('pytest_asyncio',)

def pytest_configure(config):
    config.option.asyncio_mode = "auto"