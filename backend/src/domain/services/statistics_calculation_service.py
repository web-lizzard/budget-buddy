from datetime import datetime  # Removed timedelta, date
from decimal import ROUND_HALF_UP, Decimal
from typing import Sequence

from domain.aggregates.budget import Budget
from domain.aggregates.statistics_record import (
    CategoryStatisticsRecord,
    StatisticsRecord,
)
from domain.aggregates.transaction import Transaction
from domain.value_objects.money import Money
from domain.value_objects.transaction_type import TransactionType


class StatisticsCalculationService:
    """Calculates statistical data based on transactions for a budget."""

    def calculate_statistics(
        self, budget: Budget, transactions: Sequence[Transaction]
    ) -> StatisticsRecord:
        """
        Calculates statistics for a given budget based on the provided transactions.
        Uses datetime objects for calculations.
        """
        # Debug: Print transactions list
        print(f"DEBUG: Received {len(transactions)} transactions")
        for i, tx in enumerate(transactions):
            print(
                f"DEBUG: Transaction {i+1}: {tx.id} - Type: {tx.transaction_type}, Amount: {tx.amount}"
            )

        # Use datetime.now() instead of utcnow()
        today = datetime.now()
        currency = budget.currency
        zero_money = Money(0, currency)

        # --- Calculate Date Ranges using datetime ---
        days_remaining = self._calculate_days_remaining(budget.end_date, today)
        num_days_in_tx_range = self._calculate_days_in_transaction_range(transactions)
        print(
            f"DEBUG: Days remaining: {days_remaining}, Days in tx range: {num_days_in_tx_range}"
        )

        # --- Initialize Accumulators (no changes needed) ---
        total_income = zero_money
        total_expenses = zero_money
        category_stats = {
            cat.id: {
                "income": zero_money,
                "expenses": zero_money,
                "limit": cat.limit.value,
            }
            for cat in budget.categories
        }
        print(f"DEBUG: Initialized with {len(category_stats)} category stats")

        # --- Process Transactions ---
        for transaction in transactions:
            print(f"DEBUG: Processing transaction: {transaction.id}")
            print(
                f"DEBUG: Transaction type: {transaction.transaction_type}, Amount: {transaction.amount}"
            )
            print(f"DEBUG: Category ID: {transaction.category_id}")

            if transaction.transaction_type == TransactionType.INCOME:
                total_income = total_income.add(transaction.amount)
                print(f"DEBUG: Added income, new total: {total_income}")
                if transaction.category_id in category_stats:
                    category_stats[transaction.category_id]["income"] = category_stats[
                        transaction.category_id
                    ]["income"].add(transaction.amount)
                    print(
                        f"DEBUG: Updated category {transaction.category_id} income: {category_stats[transaction.category_id]['income']}"
                    )
            elif transaction.transaction_type == TransactionType.EXPENSE:
                # Expenses are stored as positive values in the system
                # For expense transactions, add the amount directly to the used_limit/total_expenses
                total_expenses = total_expenses.add(transaction.amount)
                print(f"DEBUG: Added expense, new total expenses: {total_expenses}")

                if transaction.category_id in category_stats:
                    category_stats[transaction.category_id]["expenses"] = (
                        category_stats[
                            transaction.category_id
                        ]["expenses"].add(transaction.amount)
                    )
                    print(
                        f"DEBUG: Updated category {transaction.category_id} expenses: {category_stats[transaction.category_id]['expenses']}"
                    )

        overall_current_balance = total_income.subtract(total_expenses)
        overall_used_limit = total_expenses
        overall_daily_average = self._safe_divide_money(
            overall_used_limit, num_days_in_tx_range
        )
        overall_daily_available = self._calculate_daily_available(
            budget.total_limit.value, overall_current_balance, days_remaining
        )

        # Debug: Print final calculations
        print(f"DEBUG: Total income: {total_income}")
        print(f"DEBUG: Total expenses: {total_expenses}")
        print(f"DEBUG: Overall current balance: {overall_current_balance}")
        print(f"DEBUG: Overall used limit: {overall_used_limit}")

        category_statistics_records = []
        for category in budget.categories:
            cat_id = category.id
            cat_data = category_stats.get(cat_id)
            if not cat_data:
                continue

            cat_income = cat_data["income"]
            cat_expenses = cat_data["expenses"]
            cat_limit = cat_data["limit"]

            cat_current_balance = cat_income.subtract(cat_expenses)
            cat_used_limit = cat_expenses
            cat_daily_average = self._safe_divide_money(
                cat_expenses, num_days_in_tx_range
            )
            cat_daily_available = self._calculate_daily_available(
                cat_limit, cat_current_balance, days_remaining
            )

            category_statistics_records.append(
                CategoryStatisticsRecord(
                    category_id=cat_id,
                    current_balance=cat_current_balance,
                    daily_available_amount=cat_daily_available,
                    daily_average=cat_daily_average,
                    used_limit=cat_used_limit,
                )
            )

        # --- Create Final Statistics Record ---
        stats_record = StatisticsRecord(
            user_id=budget.user_id,
            budget_id=budget.id,
            current_balance=overall_current_balance,
            daily_available_amount=overall_daily_available,
            daily_average=overall_daily_average,
            used_limit=overall_used_limit,
            categories_statistics=category_statistics_records,
        )

        print(f"DEBUG: Created statistics record: {stats_record}")
        print(f"DEBUG: Used limit in record: {stats_record.used_limit}")
        return stats_record

    def _calculate_days_remaining(self, end_date_dt: datetime, today: datetime) -> int:
        """Calculates remaining calendar days using datetime, minimum 1."""
        # Use datetime.now() logic here as well if consistency is desired, but `today` is passed in
        delta = end_date_dt - today
        if delta.total_seconds() < 0:
            return 1
        return delta.days + 1

    def _calculate_days_in_transaction_range(
        self, transactions: Sequence[Transaction]
    ) -> int:
        """Calculates the number of calendar days spanned by transactions using datetime, min 1."""
        if not transactions:
            return 1
        dates = [
            tx.occurred_date
            for tx in transactions
            if hasattr(tx, "occurred_date") and tx.occurred_date
        ]
        if not dates:
            return 1
        min_date = min(dates)
        max_date = max(dates)
        delta = max_date - min_date
        return delta.days + 1

    def _safe_divide_money(self, money: Money, days: int) -> Money:
        """Divides Money amount (smallest units) by days, returning Money(0,...) on error."""
        if days <= 0:
            return Money(0, money.currency)
        try:
            daily_amount_decimal = (Decimal(money.amount) / Decimal(days)).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
            daily_amount_int = int(daily_amount_decimal)
            return Money(daily_amount_int, money.currency)
        except Exception:
            return Money(0, money.currency)

    def _calculate_daily_available(
        self, limit: Money, current_balance: Money, days_remaining: int
    ) -> Money:
        """Calculates daily available amount based on current balance and days remaining.
        It computes (limit + current_balance) / days_remaining.
        """
        # Ensure currencies match
        if limit.currency != current_balance.currency:
            return Money(0, limit.currency)

        total_available = limit.add(current_balance)
        if total_available.amount < 0:
            # No budget available
            return Money(0, limit.currency)

        return self._safe_divide_money(total_available, days_remaining)
