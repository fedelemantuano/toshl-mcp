import logging
from contextlib import asynccontextmanager
from typing import Any

from mcp.server.fastmcp import FastMCP

from toshl_mcp import tools
from toshl_mcp.client import ToshlClient
from toshl_mcp.config import get_settings
from toshl_mcp.logging_utils import logging_context

logger = logging.getLogger(__name__)

# Module-level client set during lifespan, used by all tools.
_client: ToshlClient | None = None


def _get_client() -> ToshlClient:
    """Return the active client or raise if the server has not started yet."""
    if _client is None:
        raise RuntimeError("ToshlClient not initialized — server not started")
    return _client


@asynccontextmanager
async def _lifespan(_server: FastMCP):  # type: ignore[type-arg]
    """Create and tear down the shared ToshlClient for the server session."""
    global _client  # noqa: PLW0603
    settings = get_settings()
    logger.info("Starting Toshl MCP server (base_url=%s)", settings.base_url)
    async with ToshlClient(settings) as client:
        _client = client
        yield
    _client = None
    logger.info("Toshl MCP server stopped")


mcp = FastMCP("Toshl Finance", lifespan=_lifespan)


@mcp.tool()
async def get_accounts() -> list[dict[str, Any]]:
    """List all Toshl accounts with their current balances and currency."""
    logger.info("MCP tool: get_accounts called")
    result = await tools.get_accounts(_get_client())
    return [a.model_dump(mode="json") for a in result]


@mcp.tool()
async def get_entries(
    from_date: str,
    to_date: str,
    category: str | None = None,
    tags: str | None = None,
) -> list[dict[str, Any]]:
    """List transactions with optional filters.

    Args:
        from_date: Start date in YYYY-MM-DD format (required).
        to_date: End date in YYYY-MM-DD format (required).
        category: Filter by category ID (optional).
        tags: Filter by tag IDs, comma-separated (optional).
    """
    logger.info("MCP tool: get_entries from=%s to=%s", from_date, to_date)
    result = await tools.get_entries(
        _get_client(), from_date, to_date, category=category, tags=tags
    )
    return [e.model_dump(mode="json") for e in result]


@mcp.tool()
async def get_categories(type: str | None = None) -> list[dict[str, Any]]:
    """List expense/income categories.

    Args:
        type: Filter by type — 'expense' or 'income' (optional, returns all if omitted).
    """
    logger.info("MCP tool: get_categories type=%s", type)
    result = await tools.get_categories(_get_client(), type=type)
    return [c.model_dump(mode="json") for c in result]


@mcp.tool()
async def get_tags() -> list[dict[str, Any]]:
    """List all Toshl tags."""
    logger.info("MCP tool: get_tags called")
    result = await tools.get_tags(_get_client())
    return [t.model_dump(mode="json") for t in result]


@mcp.tool()
async def get_budgets() -> list[dict[str, Any]]:
    """List all budgets with their limits and current spending status."""
    logger.info("MCP tool: get_budgets called")
    result = await tools.get_budgets(_get_client())
    return [b.model_dump(mode="json") for b in result]


@mcp.tool()
async def get_summary(from_date: str, to_date: str) -> dict[str, Any]:
    """Get aggregated spending/income statistics for a date range.

    Args:
        from_date: Start date in YYYY-MM-DD format.
        to_date: End date in YYYY-MM-DD format.
    """
    logger.info("MCP tool: get_summary from=%s to=%s", from_date, to_date)
    result = await tools.get_summary(_get_client(), from_date, to_date)
    return result.model_dump(mode="json")


def main() -> None:
    """Start the MCP server on stdio transport with async-safe logging to stderr."""
    root_logger = logging.getLogger()
    with logging_context(root_logger, verbose=0):
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
