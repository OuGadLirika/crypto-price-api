import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from app.db.engine import Base
from app.repositories.currency_repository import CurrencyRepository
from datetime import datetime


@pytest_asyncio.fixture
async def test_db_engine():
    """Create an in-memory SQLite async engine for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_db_engine):
    """Provide a test session."""
    session_factory = async_sessionmaker(bind=test_db_engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session


@pytest.mark.asyncio
async def test_currency_repository_add_and_list(test_session):
    repo = CurrencyRepository(test_session)
    
    # Add a record
    now = datetime.now()
    entity = await repo.add(currency="btc", date_=now, price=50000.123)
    await test_session.commit()
    
    assert entity.id is not None
    assert entity.currency == "btc"
    assert entity.price == 50000.123
    
    # List paginated
    items, total = await repo.list_paginated(page=1, page_size=10)
    assert total == 1
    assert len(items) == 1
    assert items[0].currency == "btc"


@pytest.mark.asyncio
async def test_currency_repository_delete_all(test_session):
    repo = CurrencyRepository(test_session)
    
    # Add records
    now = datetime.now()
    await repo.add(currency="btc", date_=now, price=50000)
    await repo.add(currency="eth", date_=now, price=3000)
    await test_session.commit()
    
    # Verify count
    items, total = await repo.list_paginated(page=1, page_size=10)
    assert total == 2
    
    # Delete all
    deleted = await repo.delete_all()
    await test_session.commit()
    assert deleted == 2
    
    # Verify empty
    items, total = await repo.list_paginated(page=1, page_size=10)
    assert total == 0
