import uuid
from datetime import datetime
from typing import Any

from domain.value_objects import BudgetStrategyType, Limit, Money, TransactionType
from domain.value_objects.budget_strategy import (
    BudgetStrategyInput,
    MonthlyBudgetStrategyInput,
    YearlyBudgetStrategyInput,
)
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    composite,
    mapped_column,
    relationship,
)

# --- ORM Composite Helper Classes ---


class ORMMoney(Money):
    """ORM-specific extension of Money for SQLAlchemy composite compatibility."""

    @classmethod
    def from_composite(cls, amount: int, currency: str) -> "ORMMoney":
        """Factory method for SQLAlchemy composite."""
        return cls(amount=amount, currency=currency)

    def __composite_values__(self):
        """Return values for SQLAlchemy composite persistence."""
        return self.amount, self.currency


class ORMLimit(Limit):
    """ORM-specific extension of Limit for SQLAlchemy compatibility"""

    @classmethod
    def from_composite(cls, amount: int, currency: str) -> "ORMLimit":
        """Factory method for SQLAlchemy composite."""
        return cls(value=ORMMoney(amount=amount, currency=currency))

    def __composite_values__(self):
        """Return values for SQLAlchemy composite persistence."""
        return self.value.amount, self.value.currency


class ORMBudgetStrategy:
    """ORM helper to map BudgetStrategyInput to/from DB columns."""

    def __init__(self, strategy_input: BudgetStrategyInput):
        self._strategy_input = strategy_input

    @classmethod
    def from_composite(
        cls, strategy_type: BudgetStrategyType, parameters: dict[str, Any] | None
    ) -> "ORMBudgetStrategy":
        """Recreate the correct BudgetStrategyInput domain object from DB data."""
        params = parameters or {}

        strategy_obj: BudgetStrategyInput
        if strategy_type == BudgetStrategyType.MONTHLY:
            strategy_obj = MonthlyBudgetStrategyInput(**params)
        elif strategy_type == BudgetStrategyType.YEARLY:
            strategy_obj = YearlyBudgetStrategyInput(**params)
        else:
            raise ValueError(f"Unsupported strategy type: {strategy_type}")

        return cls(strategy_obj)

    def __composite_values__(self):
        """Extract DB values (type enum, parameters dict) from the domain object."""
        strategy_type = self._strategy_input.strategy_type
        if isinstance(self._strategy_input, MonthlyBudgetStrategyInput):
            parameters = {"start_day": self._strategy_input.start_day}
        elif isinstance(self._strategy_input, YearlyBudgetStrategyInput):
            parameters = {
                "start_month": self._strategy_input.start_month,
                "start_day": self._strategy_input.start_day,
            }
        else:
            parameters = None  # Or empty dict {}
        return strategy_type, parameters

    # Optional: Allow direct access to the underlying domain object
    @property
    def strategy_input(self) -> BudgetStrategyInput:
        return self._strategy_input


# --- Base Class ---
class Base(DeclarativeBase):
    pass


# --- Model Definitions ---


class BudgetModel(Base):
    __tablename__ = "budgets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Composite mapping for total_limit (Limit value object)
    _total_limit_amount: Mapped[int] = mapped_column(
        "total_limit_amount", Integer, nullable=False
    )
    _total_limit_currency: Mapped[str] = mapped_column(
        "total_limit_currency", String(3), nullable=False
    )
    total_limit: Mapped[Limit] = composite(
        ORMLimit.from_composite,  # Use the correct factory
        _total_limit_amount,
        _total_limit_currency,
    )

    # Strategy mapping (Composite)
    _strategy_type_db: Mapped[BudgetStrategyType] = mapped_column(
        "strategy_type",  # Maps to the strategy_type column in DB
        SQLAlchemyEnum(
            BudgetStrategyType,
            name="budget_strategy_type_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    _strategy_parameters: Mapped[dict | None] = mapped_column(
        "strategy_parameters", JSONB, nullable=True
    )
    strategy: Mapped[ORMBudgetStrategy] = composite(
        ORMBudgetStrategy.from_composite,
        _strategy_type_db,
        _strategy_parameters,
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deactivation_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    # Timestamps (as DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    categories: Mapped[list["CategoryModel"]] = relationship(
        "CategoryModel",
        back_populates="budget",
        cascade="all, delete-orphan",
    )
    statistics_records: Mapped[list["StatisticsRecordModel"]] = relationship(
        "StatisticsRecordModel",
        back_populates="budget",
        cascade="all, delete-orphan",
    )
    user: Mapped["UserModel"] = relationship(back_populates="budgets")

    __mapper_args__ = {"eager_defaults": True}


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    budget_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("budgets.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Composite mapping for limit (Limit value object) - CORRECTED
    _limit_amount: Mapped[int] = mapped_column("limit_amount", Integer, nullable=False)
    _limit_currency: Mapped[str] = mapped_column(
        "limit_currency", String(3), nullable=False
    )
    limit: Mapped[Limit] = composite(
        ORMLimit.from_composite,
        _limit_amount,
        _limit_currency,
    )

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    # Timestamps (as DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    budget: Mapped["BudgetModel"] = relationship(
        "BudgetModel", back_populates="categories"
    )
    transactions: Mapped[list["TransactionModel"]] = relationship(
        "TransactionModel",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    category_statistics_records: Mapped[list["CategoryStatisticsRecordModel"]] = (
        relationship(
            "CategoryStatisticsRecordModel",
            back_populates="category",
            cascade="all, delete-orphan",
        )
    )
    user: Mapped["UserModel"] = relationship(back_populates="categories")

    __mapper_args__ = {"eager_defaults": True}


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    # Composite mapping for amount (Money value object) - UPDATED
    _amount_amount: Mapped[int] = mapped_column(
        "amount_amount", Integer, nullable=False
    )
    _amount_currency: Mapped[str] = mapped_column(
        "amount_currency", String(3), nullable=False
    )
    amount: Mapped[Money] = composite(  # Use ORMMoney
        ORMMoney.from_composite,
        _amount_amount,
        _amount_currency,
    )

    transaction_type: Mapped[TransactionType] = mapped_column(
        SQLAlchemyEnum(
            TransactionType,
            name="transaction_type_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    occurred_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    # Timestamps (as DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel", back_populates="transactions"
    )
    user: Mapped["UserModel"] = relationship(back_populates="transactions")

    __mapper_args__ = {"eager_defaults": True}


class StatisticsRecordModel(Base):
    __tablename__ = "statistics_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    budget_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    # Link to the transaction that generated this record (optional)
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "transactions.id", ondelete="SET NULL"
        ),  # Link to transaction, set NULL if transaction is deleted
        nullable=True,
        index=True,  # Index for faster lookups
        unique=True,  # Assuming one stats record per transaction
    )

    # Composite mapping for current_balance - UPDATED
    _current_balance_amount: Mapped[int] = mapped_column(
        "current_balance_amount", Integer, nullable=False
    )
    _current_balance_currency: Mapped[str] = mapped_column(
        "current_balance_currency", String(3), nullable=False
    )
    current_balance: Mapped[Money] = composite(  # Use ORMMoney
        ORMMoney.from_composite, _current_balance_amount, _current_balance_currency
    )

    # Composite mapping for daily_available_amount - UPDATED
    _daily_available_amount_amount: Mapped[int] = mapped_column(
        "daily_available_amount_amount", Integer, nullable=False
    )
    _daily_available_amount_currency: Mapped[str] = mapped_column(
        "daily_available_amount_currency", String(3), nullable=False
    )
    daily_available_amount: Mapped[Money] = composite(  # Use ORMMoney
        ORMMoney.from_composite,
        _daily_available_amount_amount,
        _daily_available_amount_currency,
    )

    # Composite mapping for daily_average - UPDATED
    _daily_average_amount: Mapped[int] = mapped_column(
        "daily_average_amount", Integer, nullable=False
    )
    _daily_average_currency: Mapped[str] = mapped_column(
        "daily_average_currency", String(3), nullable=False
    )
    daily_average: Mapped[Money] = composite(  # Use ORMMoney
        ORMMoney.from_composite, _daily_average_amount, _daily_average_currency
    )

    # Composite mapping for used_limit - UPDATED
    _used_limit_amount: Mapped[int] = mapped_column(
        "used_limit_amount", Integer, nullable=False
    )
    _used_limit_currency: Mapped[str] = mapped_column(
        "used_limit_currency", String(3), nullable=False
    )
    used_limit: Mapped[Money] = composite(  # Use ORMMoney
        ORMMoney.from_composite, _used_limit_amount, _used_limit_currency
    )

    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    # Timestamps (as DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    budget: Mapped["BudgetModel"] = relationship(
        "BudgetModel", back_populates="statistics_records"
    )
    category_statistics: Mapped[list["CategoryStatisticsRecordModel"]] = relationship(
        "CategoryStatisticsRecordModel",
        back_populates="statistics_record",
        cascade="all, delete-orphan",
    )
    user: Mapped["UserModel"] = relationship(back_populates="statistics_records")

    __mapper_args__ = {"eager_defaults": True}


class CategoryStatisticsRecordModel(Base):
    __tablename__ = "category_statistics_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    statistics_record_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("statistics_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    # Composite mapping for current_balance - UPDATED
    _cat_current_balance_amount: Mapped[int] = mapped_column(
        "current_balance_amount", Integer, nullable=False
    )
    _cat_current_balance_currency: Mapped[str] = mapped_column(
        "current_balance_currency", String(3), nullable=False
    )
    current_balance: Mapped[Money] = composite(  # Use ORMMoney
        ORMMoney.from_composite,
        _cat_current_balance_amount,
        _cat_current_balance_currency,
    )

    # Composite mapping for daily_available_amount - UPDATED
    _cat_daily_available_amount_amount: Mapped[int] = mapped_column(
        "daily_available_amount_amount", Integer, nullable=False
    )
    _cat_daily_available_amount_currency: Mapped[str] = mapped_column(
        "daily_available_amount_currency", String(3), nullable=False
    )
    daily_available_amount: Mapped[Money] = composite(  # Use ORMMoney
        ORMMoney.from_composite,
        _cat_daily_available_amount_amount,
        _cat_daily_available_amount_currency,
    )

    # Composite mapping for daily_average - UPDATED
    _cat_daily_average_amount: Mapped[int] = mapped_column(
        "daily_average_amount", Integer, nullable=False
    )
    _cat_daily_average_currency: Mapped[str] = mapped_column(
        "daily_average_currency", String(3), nullable=False
    )
    daily_average: Mapped[Money] = composite(  # Use ORMMoney
        ORMMoney.from_composite, _cat_daily_average_amount, _cat_daily_average_currency
    )

    # Composite mapping for used_limit - UPDATED
    _cat_used_limit_amount: Mapped[int] = mapped_column(
        "used_limit_amount", Integer, nullable=False
    )
    _cat_used_limit_currency: Mapped[str] = mapped_column(
        "used_limit_currency", String(3), nullable=False
    )
    used_limit: Mapped[Money] = composite(  # Use ORMMoney
        ORMMoney.from_composite, _cat_used_limit_amount, _cat_used_limit_currency
    )

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    # Timestamps (as DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    statistics_record: Mapped["StatisticsRecordModel"] = relationship(
        "StatisticsRecordModel", back_populates="category_statistics"
    )
    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel", back_populates="category_statistics_records"
    )
    user: Mapped["UserModel"] = relationship(
        back_populates="category_statistics_records"
    )

    __mapper_args__ = {"eager_defaults": True}


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    budgets: Mapped[list["BudgetModel"]] = relationship(back_populates="user")
    categories: Mapped[list["CategoryModel"]] = relationship(back_populates="user")
    transactions: Mapped[list["TransactionModel"]] = relationship(back_populates="user")
    statistics_records: Mapped[list["StatisticsRecordModel"]] = relationship(
        back_populates="user"
    )
    category_statistics_records: Mapped[list["CategoryStatisticsRecordModel"]] = (
        relationship(back_populates="user")
    )

    __mapper_args__ = {"eager_defaults": True}
