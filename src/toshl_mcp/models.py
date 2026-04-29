from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Currency(BaseModel):
    """Monetary currency with optional exchange rate metadata."""

    code: str
    rate: float | None = None
    main_rate: float | None = None
    fixed: bool = False


class Account(BaseModel):
    """Toshl account with current balance."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    balance: float
    initial_balance: float = 0.0
    currency: Currency
    type: str = "regular"
    status: str = "active"


class Entry(BaseModel):
    """Single financial transaction — negative amount = expense, positive = income."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    amount: float
    currency: Currency
    date: date
    desc: str | None = None
    account: str
    category: str | None = None
    tags: list[str] = Field(default_factory=list)


class Category(BaseModel):
    """Expense or income category used to classify entries."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    type: Literal["expense", "income"]
    deleted: bool = False


class Tag(BaseModel):
    """User-defined label for cross-cutting classification of entries."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    type: Literal["expense", "income"]


class Budget(BaseModel):
    """Spending limit for a time period with current consumption tracked by Toshl."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    limit: float
    spent: float = 0.0
    currency: Currency
    from_date: date = Field(alias="from")
    to_date: date = Field(alias="to")


class Summary(BaseModel):
    """Aggregated spending statistics computed locally from a set of entries."""

    from_date: str
    to_date: str
    total_expenses: float
    total_income: float
    net: float
    avg_daily_expense: float
    period_days: int
    entry_count: int
