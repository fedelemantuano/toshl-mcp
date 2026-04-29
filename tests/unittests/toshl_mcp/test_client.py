import base64
from collections.abc import AsyncGenerator

import httpx
import pytest
import respx
from tenacity import stop_after_attempt, wait_none

from toshl_mcp.client import ToshlClient
from toshl_mcp.config import Settings
from toshl_mcp.models import Account, Budget, Category, Entry, Tag


def _settings() -> Settings:
    return Settings(toshl_token="testtoken123")


def _fast_client() -> ToshlClient:
    """Client with no retry wait for tests."""
    return ToshlClient(
        _settings(), retry_wait=wait_none(), retry_stop=stop_after_attempt(3)
    )


def _account_data(id: str = "1") -> dict:
    return {
        "id": id,
        "name": f"Account {id}",
        "balance": 100.0,
        "currency": {"code": "EUR", "fixed": False},
    }


def _entry_data(id: str = "1") -> dict:
    return {
        "id": id,
        "amount": -10.0,
        "currency": {"code": "EUR", "fixed": False},
        "date": "2024-01-15",
        "account": "acc1",
    }


def _category_data(id: str = "1") -> dict:
    return {"id": id, "name": "Food", "type": "expense"}


def _tag_data(id: str = "1") -> dict:
    return {"id": id, "name": "Work", "type": "expense"}


def _budget_data(id: str = "1") -> dict:
    return {
        "id": id,
        "name": "Food budget",
        "limit": 300.0,
        "spent": 50.0,
        "currency": {"code": "EUR", "fixed": False},
        "from": "2024-01-01",
        "to": "2024-01-31",
    }


@pytest.fixture
async def client() -> AsyncGenerator[ToshlClient]:
    async with _fast_client() as c:
        yield c


class TestAuth:
    async def test_basic_auth_header(self, client: ToshlClient) -> None:
        expected = "Basic " + base64.b64encode(b"testtoken123:").decode()
        with respx.mock(base_url="https://api.toshl.com") as mock:
            mock.get("/accounts").respond(
                200, json=[_account_data()], headers={"X-Total-Count": "1"}
            )
            await client.get_accounts()
            assert mock.calls[0].request.headers["authorization"] == expected


class TestPagination:
    async def test_single_page(self, client: ToshlClient) -> None:
        with respx.mock(base_url="https://api.toshl.com") as mock:
            mock.get("/accounts").respond(
                200,
                json=[_account_data("1"), _account_data("2")],
                headers={"X-Total-Count": "2"},
            )
            result = await client.get_accounts()
            assert len(result) == 2
            assert len(mock.calls) == 1

    async def test_multi_page(self, client: ToshlClient) -> None:
        page0 = [_account_data(str(i)) for i in range(200)]
        page1 = [_account_data(str(i)) for i in range(200, 250)]

        with respx.mock(base_url="https://api.toshl.com") as mock:
            mock.get("/accounts").mock(
                side_effect=[
                    httpx.Response(200, json=page0, headers={"X-Total-Count": "250"}),
                    httpx.Response(200, json=page1, headers={"X-Total-Count": "250"}),
                ]
            )
            result = await client.get_accounts()
            assert len(result) == 250
            assert len(mock.calls) == 2

    async def test_empty_result(self, client: ToshlClient) -> None:
        with respx.mock(base_url="https://api.toshl.com") as mock:
            mock.get("/accounts").respond(200, json=[], headers={"X-Total-Count": "0"})
            result = await client.get_accounts()
            assert result == []
            assert len(mock.calls) == 1

    async def test_missing_total_count_header(self, client: ToshlClient) -> None:
        with respx.mock(base_url="https://api.toshl.com") as mock:
            mock.get("/accounts").respond(200, json=[_account_data()])
            result = await client.get_accounts()
            assert len(result) == 1


class TestRetry:
    async def test_429_retries_and_succeeds(self) -> None:
        async with _fast_client() as client:
            with respx.mock(base_url="https://api.toshl.com") as mock:
                mock.get("/accounts").mock(
                    side_effect=[
                        httpx.Response(429),
                        httpx.Response(
                            200, json=[_account_data()], headers={"X-Total-Count": "1"}
                        ),
                    ]
                )
                result = await client.get_accounts()
                assert len(result) == 1
                assert len(mock.calls) == 2

    async def test_500_retries_and_succeeds(self) -> None:
        async with _fast_client() as client:
            with respx.mock(base_url="https://api.toshl.com") as mock:
                mock.get("/accounts").mock(
                    side_effect=[
                        httpx.Response(500),
                        httpx.Response(
                            200, json=[_account_data()], headers={"X-Total-Count": "1"}
                        ),
                    ]
                )
                result = await client.get_accounts()
                assert len(result) == 1

    async def test_404_does_not_retry(self) -> None:
        async with _fast_client() as client:
            with respx.mock(base_url="https://api.toshl.com") as mock:
                mock.get("/accounts").respond(404)
                with pytest.raises(httpx.HTTPStatusError):
                    await client.get_accounts()
                assert len(mock.calls) == 1

    async def test_max_retries_exceeded_reraises(self) -> None:
        async with ToshlClient(
            _settings(), retry_wait=wait_none(), retry_stop=stop_after_attempt(2)
        ) as client:
            with respx.mock(base_url="https://api.toshl.com") as mock:
                mock.get("/accounts").respond(503)
                with pytest.raises(httpx.HTTPStatusError):
                    await client.get_accounts()
                assert len(mock.calls) == 2


class TestEndpoints:
    async def test_get_accounts(self, client: ToshlClient) -> None:
        with respx.mock(base_url="https://api.toshl.com") as mock:
            mock.get("/accounts").respond(
                200, json=[_account_data()], headers={"X-Total-Count": "1"}
            )
            result = await client.get_accounts()
            assert len(result) == 1
            assert isinstance(result[0], Account)

    async def test_get_entries_passes_filters(self, client: ToshlClient) -> None:
        with respx.mock(base_url="https://api.toshl.com") as mock:
            route = mock.get("/entries").respond(
                200, json=[_entry_data()], headers={"X-Total-Count": "1"}
            )
            await client.get_entries(
                "2024-01-01", "2024-01-31", category="42", tags="1,2"
            )
            params = dict(route.calls[0].request.url.params)
            assert params["from"] == "2024-01-01"
            assert params["to"] == "2024-01-31"
            assert params["category"] == "42"
            assert params["tags"] == "1,2"

    async def test_get_entries_returns_entries(self, client: ToshlClient) -> None:
        with respx.mock(base_url="https://api.toshl.com") as mock:
            mock.get("/entries").respond(
                200, json=[_entry_data()], headers={"X-Total-Count": "1"}
            )
            result = await client.get_entries("2024-01-01", "2024-01-31")
            assert isinstance(result[0], Entry)

    async def test_get_categories_type_filter(self, client: ToshlClient) -> None:
        with respx.mock(base_url="https://api.toshl.com") as mock:
            route = mock.get("/categories").respond(
                200, json=[_category_data()], headers={"X-Total-Count": "1"}
            )
            result = await client.get_categories(type="expense")
            assert isinstance(result[0], Category)
            params = dict(route.calls[0].request.url.params)
            assert params["type"] == "expense"

    async def test_get_tags(self, client: ToshlClient) -> None:
        with respx.mock(base_url="https://api.toshl.com") as mock:
            mock.get("/tags").respond(
                200, json=[_tag_data()], headers={"X-Total-Count": "1"}
            )
            result = await client.get_tags()
            assert isinstance(result[0], Tag)

    async def test_get_budgets(self, client: ToshlClient) -> None:
        with respx.mock(base_url="https://api.toshl.com") as mock:
            mock.get("/budgets").respond(
                200, json=[_budget_data()], headers={"X-Total-Count": "1"}
            )
            result = await client.get_budgets()
            assert isinstance(result[0], Budget)
            assert result[0].spent == 50.0


class TestIsRetryable:
    async def test_transport_error_retries_and_succeeds(self) -> None:
        async with _fast_client() as client:
            with respx.mock(base_url="https://api.toshl.com") as mock:
                mock.get("/accounts").mock(
                    side_effect=[
                        httpx.ConnectError("connection refused"),
                        httpx.Response(
                            200,
                            json=[_account_data()],
                            headers={"X-Total-Count": "1"},
                        ),
                    ]
                )
                result = await client.get_accounts()
                assert len(result) == 1
                assert len(mock.calls) == 2


class TestEndpointFilters:
    async def test_get_entries_with_account_filter(self, client: ToshlClient) -> None:
        with respx.mock(base_url="https://api.toshl.com") as mock:
            route = mock.get("/entries").respond(
                200, json=[_entry_data()], headers={"X-Total-Count": "1"}
            )
            await client.get_entries("2024-01-01", "2024-01-31", account="acc1")
            params = dict(route.calls[0].request.url.params)
            assert params["account"] == "acc1"


class TestContextManager:
    async def test_not_initialized_raises(self) -> None:
        client = _fast_client()
        with pytest.raises(RuntimeError, match="context manager"):
            await client.get_accounts()
