import logging

from domain.exceptions.budget_not_found_error import BudgetNotFoundError
from domain.exceptions.category_not_found_error import CategoryNotFoundError
from domain.exceptions.domain_exception import DomainError
from domain.exceptions.not_compatible_version_error import NotCompatibleVersionError
from domain.exceptions.statistics_record_not_found_error import (
    StatisticsRecordNotFoundError,
)
from domain.exceptions.transaction_not_found_error import TransactionNotFoundError
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

# Configure logging
_logger = logging.getLogger(__name__)


class UnknownException(DomainError):
    """Exception for unknown errors."""

    def __init__(self, message: str = "An unknown error occurred"):
        super().__init__(message)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            return await call_next(request)
        except NotCompatibleVersionError as e:
            return self._create_error_response(e, status_code=status.HTTP_409_CONFLICT)
        except (
            BudgetNotFoundError,
            CategoryNotFoundError,
            TransactionNotFoundError,
            StatisticsRecordNotFoundError,
        ) as e:
            return self._create_error_response(e, status_code=status.HTTP_404_NOT_FOUND)
        except DomainError as e:
            return self._create_error_response(
                e, status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            _logger.debug(exc_info=e, msg=str(e))
            return self._create_error_response(
                UnknownException(str(e)),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_error_response(
        self, exc: DomainError, status_code: int
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"status": exc.status, "message": exc.message},
        )
