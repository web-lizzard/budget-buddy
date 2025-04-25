from application.dtos import BudgetDTO
from application.queries.get_budget_by_id_query import GetBudgetByIdQuery
from application.queries.handlers import QueryHandler


class GetBudgetQueryHandler(QueryHandler[GetBudgetByIdQuery]):
    async def handle(self, query: GetBudgetByIdQuery) -> BudgetDTO:
        raise NotImplementedError
