from app.services.validation import CurrencyValidator
import pytest


@pytest.mark.parametrize("value", ["BTC", "eth", "ioi", "USDT", "SOL1", "A1B2C3"])
def test_currency_validator_ok(value):
    out = CurrencyValidator.normalize_and_validate(value)
    assert out == value.upper()


@pytest.mark.parametrize("value", ["", " ", "b", "TOO_LONG_SYMBOL_123456", "bad-coin", "рус", "usd$", "a*b"])
def test_currency_validator_bad(value):
    with pytest.raises(ValueError):
        CurrencyValidator.normalize_and_validate(value)
