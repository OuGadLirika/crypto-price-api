from __future__ import annotations

import re


class CurrencyValidator:
    _pattern = re.compile(r"^[A-Z0-9]{2,15}$")

    @classmethod
    def normalize_and_validate(cls, raw: str) -> str:
        candidate = (raw or "").strip().upper()
        if not cls._pattern.match(candidate):
            raise ValueError("invalid currency")
        return candidate
