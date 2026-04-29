import logging
import math
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)
from tenacity.wait import wait_base

from toshl_mcp.config import Settings
from toshl_mcp.models import Account, Budget, Category, Entry, Tag

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
_PER_PAGE = 200


def _is_retryable(exc: BaseException) -> bool:
    """Return True for transient server errors and rate limits worth retrying."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _RETRYABLE_STATUS
    return isinstance(exc, httpx.TransportError)


class ToshlClient:
    """Async HTTP client for the Toshl Finance REST API.

    Must be used as an async context manager to manage the underlying
    httpx connection pool. Retries transient failures automatically via
    tenacity and paginates all list endpoints transparently.
    """

    def __init__(
        self,
        settings: Settings,
        *,
        retry_wait: wait_base | None = None,
        retry_stop: Any = None,
    ) -> None:
        """Initialise client with optional retry overrides (useful in tests).

        Args:
            settings: Server configuration including the Toshl token.
            retry_wait: Tenacity wait strategy; defaults to exponential back-off.
            retry_stop: Tenacity stop strategy; defaults to 4 attempts.
        """
        self._settings = settings
        self._retry_wait: wait_base = retry_wait or wait_exponential(
            multiplier=1, min=1, max=30
        )
        self._retry_stop = retry_stop or stop_after_attempt(4)
        self._http: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "ToshlClient":
        """Open the underlying httpx connection pool."""
        self._http = httpx.AsyncClient(
            base_url=self._settings.base_url,
            auth=httpx.BasicAuth(username=self._settings.toshl_token, password=""),
            headers={"Accept": "application/json"},
            timeout=30.0,
        )
        logger.debug("ToshlClient HTTP session opened")
        return self

    async def __aexit__(self, *args: object) -> None:
        """Close the underlying httpx connection pool."""
        if self._http is not None:
            await self._http.aclose()
            logger.debug("ToshlClient HTTP session closed")

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Execute a single HTTP request with automatic retry on transient errors."""
        if self._http is None:
            raise RuntimeError("ToshlClient must be used as async context manager")
        async for attempt in AsyncRetrying(
            retry=retry_if_exception(_is_retryable),
            wait=self._retry_wait,
            stop=self._retry_stop,
            reraise=True,
        ):
            with attempt:
                logger.debug("%s %s params=%s", method, path, kwargs.get("params"))
                response = await self._http.request(method, path, **kwargs)
                response.raise_for_status()
                return response
        raise RuntimeError("Request failed after all retries")  # pragma: no cover

    async def _get_all_pages(
        self, path: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Fetch all pages of a paginated endpoint sequentially.

        Sequential (not concurrent) to avoid burning the rate-limit budget.
        Uses X-Total-Count header to determine total number of pages.
        """
        base_params: dict[str, Any] = {
            **(params or {}),
            "per_page": _PER_PAGE,
            "page": 0,
        }
        response = await self._request("GET", path, params=base_params)
        data: list[dict[str, Any]] = response.json()
        total = int(response.headers.get("X-Total-Count", len(data)))
        logger.debug(
            "GET %s: total=%d fetched first page (%d items)", path, total, len(data)
        )

        results = list(data)
        total_pages = math.ceil(total / _PER_PAGE)

        for page in range(1, total_pages):
            page_params = {**base_params, "page": page}
            page_response = await self._request("GET", path, params=page_params)
            page_data: list[dict[str, Any]] = page_response.json()
            results.extend(page_data)
            logger.debug("GET %s page=%d fetched %d items", path, page, len(page_data))

        return results

    async def get_accounts(self) -> list[Account]:
        """Return all accounts including archived ones."""
        logger.info("Fetching accounts")
        data = await self._get_all_pages("/accounts")
        accounts = [Account.model_validate(item) for item in data]
        logger.info("Fetched %d accounts", len(accounts))
        return accounts

    async def get_entries(
        self,
        from_date: str,
        to_date: str,
        *,
        category: str | None = None,
        tags: str | None = None,
        account: str | None = None,
    ) -> list[Entry]:
        """Return transactions in the given date range with optional filters.

        Args:
            from_date: Start date in YYYY-MM-DD format (inclusive).
            to_date: End date in YYYY-MM-DD format (inclusive).
            category: Filter by category ID.
            tags: Filter by tag IDs, comma-separated.
            account: Filter by account ID.
        """
        logger.info("Fetching entries from=%s to=%s", from_date, to_date)
        params: dict[str, Any] = {"from": from_date, "to": to_date}
        if category is not None:
            params["category"] = category
        if tags is not None:
            params["tags"] = tags
        if account is not None:
            params["account"] = account
        data = await self._get_all_pages("/entries", params)
        entries = [Entry.model_validate(item) for item in data]
        logger.info("Fetched %d entries", len(entries))
        return entries

    async def get_categories(self, *, type: str | None = None) -> list[Category]:
        """Return all categories, optionally filtered to 'expense' or 'income'."""
        logger.info("Fetching categories type=%s", type)
        params: dict[str, Any] = {}
        if type is not None:
            params["type"] = type
        data = await self._get_all_pages("/categories", params or None)
        categories = [Category.model_validate(item) for item in data]
        logger.info("Fetched %d categories", len(categories))
        return categories

    async def get_tags(self) -> list[Tag]:
        """Return all user-defined tags."""
        logger.info("Fetching tags")
        data = await self._get_all_pages("/tags")
        tags = [Tag.model_validate(item) for item in data]
        logger.info("Fetched %d tags", len(tags))
        return tags

    async def get_budgets(self) -> list[Budget]:
        """Return all budgets with current period spending included."""
        logger.info("Fetching budgets")
        data = await self._get_all_pages("/budgets")
        budgets = [Budget.model_validate(item) for item in data]
        logger.info("Fetched %d budgets", len(budgets))
        return budgets
