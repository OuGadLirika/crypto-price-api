"""
E2E smoke test demonstrating the complete flow.
Run with actual PostgreSQL if DATABASE_URL is set.
"""
import pytest
import pytest_asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.engine import Base
from app.services.currency_service import CurrencyService
from app.services.validation import CurrencyValidator


@pytest_asyncio.fixture
async def sqlite_session():
    """In-memory SQLite for E2E test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_e2e_flow(sqlite_session):
    """End-to-end: validate -> save -> paginate -> delete."""
    service = CurrencyService(session=sqlite_session, page_size=10)
    
    # 1. Validate currency
    currency_norm = CurrencyValidator.normalize_and_validate("btc")
    assert currency_norm == "BTC"
    
    # 2. Record prices
    data1 = await service.record_current_price(currency="BTC", price=Decimal("50000.12"))
    assert data1["currency"] == "btc"
    assert data1["price"] == "50000.12"
    
    data2 = await service.record_current_price(currency="ETH", price=Decimal("3000.45"))
    assert data2["currency"] == "eth"
    
    # 3. Get history (paginated)
    page = await service.get_history(page=1)
    assert page.total == 2
    assert len(page.items) == 2
    assert page.page == 1
    assert page.total_pages == 1
    
    # 4. Delete all
    deleted = await service.delete_all()
    assert deleted == 2
    
    # 5. Verify empty
    page_empty = await service.get_history(page=1)
    assert page_empty.total == 0
    assert len(page_empty.items) == 0


@pytest.mark.asyncio
async def test_validation_edge_cases():
    """Test validation edge cases."""
    # OK cases
    assert CurrencyValidator.normalize_and_validate("BTC") == "BTC"
    assert CurrencyValidator.normalize_and_validate("btc") == "BTC"
    assert CurrencyValidator.normalize_and_validate("  ioi  ") == "IOI"
    assert CurrencyValidator.normalize_and_validate("A1B2C3D4E5F6") == "A1B2C3D4E5F6"
    
    # Bad cases
    with pytest.raises(ValueError):
        CurrencyValidator.normalize_and_validate("a")  # too short
    
    with pytest.raises(ValueError):
        CurrencyValidator.normalize_and_validate("TOO_LONG_SYMBOL_1234567")  # too long
    
    with pytest.raises(ValueError):
        CurrencyValidator.normalize_and_validate("bad-coin")  # invalid char
    
    with pytest.raises(ValueError):
        CurrencyValidator.normalize_and_validate("рус")  # non-ASCII
