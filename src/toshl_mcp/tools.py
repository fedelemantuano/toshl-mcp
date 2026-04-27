import logging
from datetime import date

from toshl_mcp.client import ToshlClient
from toshl_mcp.models import Account, Budget, Category, Entry, Summary, Tag

logger = logging.getLogger(__name__)


async def get_accounts(client: ToshlClient) -> list[Account]:
    """Return all accounts including their current balances."""
    logger.info("Tool: get_accounts")
    result = await client.get_accounts()
    logger.info("Tool: get_accounts returned %d accounts", len(result))
    return result


async def get_entries(
    client: ToshlClient,
    from_date: str,
    to_date: str,
    *,
    category: str | None = None,
    tags: str | None = None,
) -> list[Entry]:
    """Return transactions in the given date range with optional category/tag filters.

    Args:
        client: Authenticated Toshl API client.
        from_date: Start date in YYYY-MM-DD format (inclusive).
        to_date: End date in YYYY-MM-DD format (inclusive).
        category: Filter by category ID.
        tags: Filter by tag IDs, comma-separated.
    """
    logger.info(
        "Tool: get_entries from=%s to=%s category=%s tags=%s",
        from_date,
        to_date,
        category,
        tags,
    )
    result = await client.get_entries(from_date, to_date, category=category, tags=tags)
    logger.info("Tool: get_entries returned %d entries", len(result))
    return result


async def get_categories(
    client: ToshlClient, *, type: str | None = None
) -> list[Category]:
    """Return all categories, optionally filtered to 'expense' or 'income'."""
    logger.info("Tool: get_categories type=%s", type)
    result = await client.get_categories(type=type)
    logger.info("Tool: get_categories returned %d categories", len(result))
    return result


async def get_tags(client: ToshlClient) -> list[Tag]:
    """Return all user-defined tags."""
    logger.info("Tool: get_tags")
    result = await client.get_tags()
    logger.info("Tool: get_tags returned %d tags", len(result))
    return result


async def get_budgets(client: ToshlClient) -> list[Budget]:
    """Return all budgets with current period spending status."""
    logger.info("Tool: get_budgets")
    result = await client.get_budgets()
    logger.info("Tool: get_budgets returned %d budgets", len(result))
    return result


async def get_summary(
    client: ToshlClient,
    from_date: str,
    to_date: str,
) -> Summary:
    """Compute aggregated expense/income statistics for the given date range.

    Fetches all entries in the range and aggregates them locally —
    Toshl has no dedicated summary endpoint.

    Args:
        client: Authenticated Toshl API client.
        from_date: Start date in YYYY-MM-DD format.
        to_date: End date in YYYY-MM-DD format.
    """
    logger.info("Tool: get_summary from=%s to=%s", from_date, to_date)
    entries = await client.get_entries(from_date, to_date)

    total_expenses = sum(abs(e.amount) for e in entries if e.amount < 0)
    total_income = sum(e.amount for e in entries if e.amount > 0)

    from_dt = date.fromisoformat(from_date)
    to_dt = date.fromisoformat(to_date)
    period_days = max((to_dt - from_dt).days, 1)

    summary = Summary(
        from_date=from_date,
        to_date=to_date,
        total_expenses=round(total_expenses, 2),
        total_income=round(total_income, 2),
        net=round(total_income - total_expenses, 2),
        avg_daily_expense=round(total_expenses / period_days, 2),
        period_days=period_days,
        entry_count=len(entries),
    )
    logger.info(
        "Tool: get_summary expenses=%.2f income=%.2f net=%.2f entries=%d",
        summary.total_expenses,
        summary.total_income,
        summary.net,
        summary.entry_count,
    )
    return summary
