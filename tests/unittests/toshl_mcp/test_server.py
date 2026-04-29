from collections.abc import Generator
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import toshl_mcp.server as server_module
from toshl_mcp.models import Account, Budget, Category, Currency, Entry, Summary, Tag
from toshl_mcp.server import mcp


def _currency() -> Currency:
    return Currency(code="EUR")


class TestToolRegistration:
    def test_all_tools_registered(self) -> None:
        tool_names = {t.name for t in mcp._tool_manager.list_tools()}
        expected = {
            "get_accounts",
            "get_entries",
            "get_categories",
            "get_tags",
            "get_budgets",
            "get_summary",
        }
        assert expected.issubset(tool_names)

    def test_tool_count(self) -> None:
        tools = mcp._tool_manager.list_tools()
        assert len(tools) >= 6


class TestGetClient:
    def test_raises_when_not_initialized(self) -> None:
        original = server_module._client
        try:
            server_module._client = None
            try:
                server_module._get_client()
                raise AssertionError("Should have raised")
            except RuntimeError as exc:
                assert "not initialized" in str(exc)
        finally:
            server_module._client = original

    def test_returns_client_when_set(self) -> None:
        mock_client = MagicMock()
        original = server_module._client
        try:
            server_module._client = mock_client
            result = server_module._get_client()
            assert result is mock_client
        finally:
            server_module._client = original


class TestLifespan:
    async def test_sets_and_clears_client(self) -> None:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        original = server_module._client
        try:
            with (
                patch("toshl_mcp.server.get_settings", return_value=MagicMock()),
                patch("toshl_mcp.server.ToshlClient", return_value=mock_client),
            ):
                async with server_module._lifespan(MagicMock()):
                    assert server_module._client is mock_client
            assert server_module._client is None
        finally:
            server_module._client = original


class TestServerTools:
    @pytest.fixture(autouse=True)
    def _set_client(self) -> Generator[MagicMock]:
        mock = MagicMock()
        original = server_module._client
        server_module._client = mock
        yield mock
        server_module._client = original

    async def test_get_accounts(self) -> None:
        accounts = [Account(id="1", name="Wallet", balance=100.0, currency=_currency())]
        with patch(
            "toshl_mcp.server.tools.get_accounts", new=AsyncMock(return_value=accounts)
        ):
            result = await server_module.get_accounts()
        assert result == [a.model_dump(mode="json") for a in accounts]

    async def test_get_entries(self) -> None:
        entries = [
            Entry(
                id="1",
                amount=-10.0,
                currency=_currency(),
                date=date(2024, 1, 15),
                account="acc1",
            )
        ]
        with patch(
            "toshl_mcp.server.tools.get_entries", new=AsyncMock(return_value=entries)
        ):
            result = await server_module.get_entries(
                "2024-01-01", "2024-01-31", category="1", tags="2"
            )
        assert result == [e.model_dump(mode="json") for e in entries]

    async def test_get_categories(self) -> None:
        cats = [Category(id="1", name="Food", type="expense")]
        with patch(
            "toshl_mcp.server.tools.get_categories", new=AsyncMock(return_value=cats)
        ):
            result = await server_module.get_categories(type="expense")
        assert result == [c.model_dump(mode="json") for c in cats]

    async def test_get_tags(self) -> None:
        tags = [Tag(id="1", name="Work", type="expense")]
        with patch("toshl_mcp.server.tools.get_tags", new=AsyncMock(return_value=tags)):
            result = await server_module.get_tags()
        assert result == [t.model_dump(mode="json") for t in tags]

    async def test_get_budgets(self) -> None:
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
        with patch(
            "toshl_mcp.server.tools.get_budgets", new=AsyncMock(return_value=budgets)
        ):
            result = await server_module.get_budgets()
        assert result == [b.model_dump(mode="json") for b in budgets]

    async def test_get_summary(self) -> None:
        summary = Summary(
            from_date="2024-01-01",
            to_date="2024-01-31",
            total_expenses=50.0,
            total_income=100.0,
            net=50.0,
            entry_count=2,
            period_days=30,
            avg_daily_expense=1.67,
        )
        with patch(
            "toshl_mcp.server.tools.get_summary", new=AsyncMock(return_value=summary)
        ):
            result = await server_module.get_summary("2024-01-01", "2024-01-31")
        assert result == summary.model_dump(mode="json")


class TestMain:
    def test_main_runs_mcp_stdio(self) -> None:
        with patch.object(server_module.mcp, "run") as mock_run:
            server_module.main()
        mock_run.assert_called_once_with(transport="stdio")
