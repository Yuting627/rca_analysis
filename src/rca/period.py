"""YYYY14MM period parsing and calendar shifts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Period:
    year: int
    month: int

    def format(self) -> str:
        return f"{self.year}14{self.month:02d}"

    def shift_months(self, delta: int) -> Period:
        idx = self.year * 12 + (self.month - 1) + delta
        year, month0 = divmod(idx, 12)
        return Period(year=year, month=month0 + 1)

    def mom(self) -> Period:
        return self.shift_months(-1)

    def yoy(self) -> Period:
        return self.shift_months(-12)


def parse_period(value: str | int) -> Period:
    s = str(value).strip()
    if len(s) != 8 or s[4:6] != "14":
        raise ValueError(f"period must be YYYY14MM, got {value!r}")
    year = int(s[0:4])
    month = int(s[6:8])
    if not 1 <= month <= 12:
        raise ValueError(f"invalid month in period {value!r}")
    return Period(year=year, month=month)


def format_period(year: int, month: int) -> str:
    return Period(year=year, month=month).format()
