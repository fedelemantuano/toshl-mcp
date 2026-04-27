from datetime import date
from unittest.mock import AsyncMock, MagicMock

from toshl_mcp.models import Account, Budget, Category, Currency, Entry, Summary, Tag
from toshl_mcp.tools import (
    get_accounts,
    get_budgets,
    get_categories,
    get_entries,
    get_summary,
    get_tags,
)


def _currency() -> Currency:
    return Currency(code="EUR")


def _make_entry(amount: float, id: str = "1") -> Entry:
    return Entry(
        id=id,
        amount=amount,
        currency=_currency(),
        date=date(2024, 1, 15),
        account="acc1",
    )


def _make_client(**method_results) -> MagicMock:
    client = MagicMock()
    for method, result in method_results.items():
        getattr(client, method).return_value = result
    for method in (
        "get_accounts",
        "get_entries",
        "get_categories",
        "get_tags",
        "get_budgets",
    ):
        if (
            not hasattr(getattr(client, method), "return_value")
            or method not in method_results
        ):
            getattr(client, method).__class__ = AsyncMock
    client.get_accounts = AsyncMock(return_value=method_results.get("get_accounts", []))
    client.get_entries = AsyncMock(return_value=method_results.get("get_entries", []))
    client.get_categories = AsyncMock(
        return_value=method_results.get("get_categories", [])
    )
    client.get_tags = AsyncMock(return_value=method_results.get("get_tags", []))
    client.get_budgets = AsyncMock(return_value=method_results.get("get_budgets", []))
    return client


class TestGetAccounts:
    async def test_returns_accounts(self) -> None:
        accounts = [Account(id="1", name="Wallet", balance=100.0, currency=_currency())]
        client = _make_client(get_accounts=accounts)
        result = await get_accounts(client)
        assert result == accounts
        client.get_accounts.assert_awaited_once()


class TestGetEntries:
    async def test_passes_filters(self) -> None:
        entries = [_make_entry(-10.0)]
        client = _make_client(get_entries=entries)
        result = await get_entries(
            client, "2024-01-01", "2024-01-31", category="42", tags="1"
        )
        assert result == entries
        client.get_entries.assert_awaited_once_with(
            "2024-01-01", "2024-01-31", category="42", tags="1"
        )

    async def test_no_filters(self) -> None:
        client = _make_client(get_entries=[])
        await get_entries(client, "2024-01-01", "2024-01-31")
        client.get_entries.assert_awaited_once_with(
            "2024-01-01", "2024-01-31", category=None, tags=None
        )


class TestGetCategories:
    async def test_passes_type_filter(self) -> None:
        cats = [Category(id="1", name="Food", type="expense")]
        client = _make_client(get_categories=cats)
        result = await get_categories(client, type="expense")
        assert result == cats
        client.get_categories.assert_awaited_once_with(type="expense")


class TestGetTags:
    async def test_returns_tags(self) -> None:
        tags = [Tag(id="1", name="Work", type="expense")]
        client = _make_client(get_tags=tags)
        result = await get_tags(client)
        assert result == tags


class TestGetBudgets:
    async def test_returns_budgets(self) -> None:
        budgets = [
            Budget.model_validate(
                {
                    "id": "1",
                    "name": "Food",
                    "limit": 300.0,
                    "currency": {"code": "EUR", "fixed": False},
                    "from": "2024-01-01",
                    "to": "2024-01-31",
                }
            )
        ]
        client = _make_client(get_budgets=budgets)
        result = await get_budgets(client)
        assert result == budgets


class TestGetSummary:
    async def test_mixed_entries(self) -> None:
        entries = [
            _make_entry(-50.0, "1"),  # expense
            _make_entry(-30.0, "2"),  # expense
            _make_entry(200.0, "3"),  # income
        ]
        client = _make_client(get_entries=entries)
        result = await get_summary(client, "2024-01-01", "2024-01-31")
        assert isinstance(result, Summary)
        assert result.total_expenses == 80.0
        assert result.total_income == 200.0
        assert result.net == 120.0
        assert result.entry_count == 3
        assert result.period_days == 30

    async def test_expenses_only(self) -> None:
        entries = [_make_entry(-100.0)]
        client = _make_client(get_entries=entries)
        result = await get_summary(client, "2024-01-01", "2024-01-31")
        assert result.total_income == 0.0
        assert result.net == -100.0

    async def test_income_only(self) -> None:
        entries = [_make_entry(500.0)]
        client = _make_client(get_entries=entries)
        result = await get_summary(client, "2024-01-01", "2024-01-31")
        assert result.total_expenses == 0.0
        assert result.net == 500.0

    async def test_empty_entries(self) -> None:
        client = _make_client(get_entries=[])
        result = await get_summary(client, "2024-01-01", "2024-01-31")
        assert result.total_expenses == 0.0
        assert result.total_income == 0.0
        assert result.entry_count == 0

    async def test_zero_day_range_clamps_to_one(self) -> None:
        entries = [_make_entry(-10.0)]
        client = _make_client(get_entries=entries)
        result = await get_summary(client, "2024-01-01", "2024-01-01")
        assert result.period_days == 1
        assert result.avg_daily_expense == 10.0

    async def test_avg_daily_expense(self) -> None:
        entries = [_make_entry(-30.0)]
        client = _make_client(get_entries=entries)
        result = await get_summary(client, "2024-01-01", "2024-01-31")
        assert result.avg_daily_expense == 1.0  # 30 / 30 days
