from rca.period import format_period, parse_period


def test_parse_format_july_2026():
    p = parse_period("20261407")
    assert p.year == 2026 and p.month == 7
    assert p.format() == "20261407"
    assert format_period(2026, 7) == "20261407"


def test_mom_yoy():
    p = parse_period("20261407")
    assert p.mom().format() == "20261406"
    assert p.yoy().format() == "20251407"
    assert parse_period("20261401").mom().format() == "20251412"
