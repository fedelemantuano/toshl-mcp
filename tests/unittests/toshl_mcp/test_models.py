from datetime import date

import pytest
from pydantic import ValidationError

from toshl_mcp.models import Account, Budget, Category, Currency, Entry, Summary, Tag


def _currency() -> Currency:
    return Currency(code="EUR", rate=1.0, fixed=False)


class TestCurrency:
    def test_basic(self) -> None:
        c = Currency(code="USD")
        assert c.code == "USD"
        assert c.rate is None
        assert c.fixed is False

    def test_full(self) -> None:
        c = Currency(code="EUR", rate=1.2, fixed=True)
        assert c.rate == 1.2
        assert c.fixed is True


class TestAccount:
    def test_basic(self) -> None:
        a = Account(
            id="1",
            name="Wallet",
            balance=100.0,
            currency=_currency(),
        )
        assert a.balance == 100.0
        assert a.status == "active"
        assert a.initial_balance == 0.0

    def test_missing_required(self) -> None:
        with pytest.raises(ValidationError):
            Account(id="1", name="x")  # type: ignore[call-arg]


class TestEntry:
    def test_expense(self) -> None:
        e = Entry(
            id="1",
            amount=-15.5,
            currency=_currency(),
            date=date(2024, 1, 1),
            account="acc1",
        )
        assert e.amount < 0
        assert e.tags == []

    def test_income(self) -> None:
        e = Entry(
            id="2",
            amount=1000.0,
            currency=_currency(),
            date=date(2024, 1, 15),
            account="acc1",
        )
        assert e.amount > 0

    def test_with_tags(self) -> None:
        e = Entry(
            id="3",
            amount=-5.0,
            currency=_currency(),
            date=date(2024, 1, 1),
            account="acc1",
            tags=["tag1", "tag2"],
        )
        assert e.tags == ["tag1", "tag2"]


class TestCategory:
    def test_expense_category(self) -> None:
        c = Category(id="1", name="Food", type="expense")
        assert c.type == "expense"
        assert c.deleted is False

    def test_income_category(self) -> None:
        c = Category(id="2", name="Salary", type="income")
        assert c.type == "income"

    def test_invalid_type(self) -> None:
        with pytest.raises(ValidationError):
            Category(id="1", name="X", type="other")  # type: ignore[arg-type]


class TestTag:
    def test_basic(self) -> None:
        t = Tag(id="1", name="Work", type="expense")
        assert t.name == "Work"


class TestBudget:
    def test_alias_fields(self) -> None:
        b = Budget.model_validate(
            {
                "id": "1",
                "name": "Food",
                "limit": 300.0,
                "spent": 150.0,
                "currency": _currency(),
                "from": "2024-01-01",
                "to": "2024-01-31",
            }
        )
        assert b.from_date == date(2024, 1, 1)
        assert b.to_date == date(2024, 1, 31)
        assert b.spent == 150.0

    def test_spent_defaults_zero(self) -> None:
        b = Budget.model_validate(
            {
                "id": "1",
                "name": "Food",
                "limit": 100.0,
                "currency": _currency(),
                "from": "2024-01-01",
                "to": "2024-01-31",
            }
        )
        assert b.spent == 0.0


class TestSummary:
    def test_net_arithmetic(self) -> None:
        s = Summary(
            from_date="2024-01-01",
            to_date="2024-01-31",
            total_expenses=200.0,
            total_income=500.0,
            net=300.0,
            avg_daily_expense=6.45,
            period_days=31,
            entry_count=10,
        )
        assert s.net == 300.0
        assert s.entry_count == 10
