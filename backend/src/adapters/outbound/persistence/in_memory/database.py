from typing import Any, Dict, Optional
from uuid import UUID

DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


class InMemoryDatabase:
    """Singleton class representing in-memory database."""

    _instance: Optional["InMemoryDatabase"] = None
    _database: Dict[str, Dict[Any, Any]] = {
        "budgets": {},  # UUID -> Tuple[int, Budget]
        "users": {DEFAULT_USER_ID: {"user_id": DEFAULT_USER_ID}},
        "transactions": {},  # UUID -> Transaction
        "statistic_records": {},  # UUID -> StatisticsRecord
    }

    def __new__(cls) -> "InMemoryDatabase":
        if cls._instance is None:
            cls._instance = super(InMemoryDatabase, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_database(cls) -> Dict[str, Dict[Any, Any]]:
        """Get the database instance."""
        return cls._database

    @classmethod
    def set_database(cls, database: Dict[str, Dict[Any, Any]]) -> None:
        """Set the database instance.

        Args:
            database: The database to set
        """
        cls._database = database


IN_MEMORY_DATABASE = InMemoryDatabase()
