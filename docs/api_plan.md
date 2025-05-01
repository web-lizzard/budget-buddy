# REST API Plan

## 1. Resources

- **Budget**: Represents a user's budget. Maps to the Budget aggregate and includes fields such as id, user_id, total_limit (with Money and Limit value object details), currency, start_date, end_date, deactivation_date, categories, and name (budget_name).
- **Category**: Represents a budget category. Maps to the Category entity and includes id, budget_id, name (category_name), and limit (Limit/Money).
- **Transaction**: Represents an income or expense record. Maps to the Transaction aggregate and includes id, category_id, amount (Money), transaction_type (INCOME/EXPENSE), occurred_date, description, and user_id.
- **StatisticsRecord**: Aggregated financial statistics for a budget, including current_balance, daily_available_amount, daily_average, and used_limit.
- **CategoryStatisticsRecord**: Detailed statistics for a single category within a budget.

## 2. Endpoints

### Budgets

- **GET /budgets**
  - **Description**: Retrieve a list of budgets.
  - **Query Parameters**:
    - `status`: Filter by 'active' or 'expired'.
    - `page`, `limit`: For pagination.
    - `sort`: Field to sort by (e.g., start_date).
  - **Response Structure**: JSON array of budget objects.
  - **Success Codes**: 200 OK
  - **Error Codes**: 404 Not Found, 409 Conflict

- **GET /budgets/{budget_id}**
  - **Description**: Retrieve detailed information for a specific budget, including its categories.
  - **Response Structure**: A budget object in JSON.
  - **Success Codes**: 200 OK
  - **Error Codes**: 404 Not Found

- **POST /budgets**
  - **Description**: Create a new budget.
  - **Request Payload**:
    ```json
    {
      "user_id": "uuid",
      "total_limit": { "amount": 1000, "currency": "USD" },
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "name": "Budget Name",
      "categories": [
         {
            "name": "Category Name",
            "limit": { "amount": 200 }
         }
      ],
      "strategy": { "type": "monthly/yearly", "parameters": {} }
    }
    ```
  - **Response**: No content; only HTTP status code 201 Created is returned.
  - **Error Codes**: 409 Conflict, 400 Bad Request, 404 Not Found

- **PATCH /budgets/{budget_id}/deactivate**
  - **Description**: Deactivate a budget to prevent automatic renewal.
  - **Response**: No content; only HTTP status code 200 OK is returned.
  - **Error Codes**: 404 Not Found

- **POST /budgets/{budget_id}/renew**
  - **Description**: Manually trigger budget renewal (if applicable), based on the defined strategy.
  - **Response**: No content; only HTTP status code 200 OK (or 202 Accepted if processed asynchronously) is returned.
  - **Error Codes**: 404 Not Found

### Categories (Nested under Budgets)

- **GET /budgets/{budget_id}/categories**
  - **Description**: Retrieve all categories associated with a specific budget.
  - **Response Structure**: JSON array of category objects.
  - **Success Codes**: 200 OK
  - **Error Codes**: 404 Not Found

- **GET /budgets/{budget_id}/categories/{category_id}**
  - **Description**: Retrieve details for a specific category in a budget.
  - **Response Structure**: A category object in JSON.
  - **Success Codes**: 200 OK
  - **Error Codes**: 404 Not Found

- **POST /budgets/{budget_id}/categories**
  - **Description**: Create a new category within a given budget.
  - **Request Payload**:
    ```json
    {
      "name": "Category Name",
      "limit": { "amount": 200 }
    }
    ```
  - **Constraints**: Maximum of 5 categories per budget; category name must be unique within a budget.
  - **Response**: No content; only HTTP status code 201 Created is returned.
  - **Error Codes**: 400 Bad Request, 409 Conflict, 404 Not Found

- **PUT /budgets/{budget_id}/categories/{category_id}**
  - **Description**: Update an existing category's details.
  - **Request Payload**:
    ```json
    {
      "name": "updated_category_name",
      "limit": { "amount": 250 }
    }
    ```
  - **Response**: No content; only HTTP status code 200 OK is returned.
  - **Error Codes**: 400 Bad Request, 404 Not Found

- **DELETE /budgets/{budget_id}/categories/{category_id}**
  - **Description**: Delete a category from a budget.
  - **Query Parameter**:
    - `transfer_policy`: Specifies how to handle transactions associated with the category ("DELETE_TRANSACTIONS" or a target category ID for "MOVE_TO_OTHER_CATEGORY").
  - **Response**: No content; only HTTP status code 200 OK is returned.
  - **Error Codes**: 400 Bad Request, 404 Not Found

### Transactions (Nested under Budgets)

- **GET /budgets/{budget_id}/transactions**
  - **Description**: Retrieve a list of transactions for a specified budget.
  - **Query Parameters**:
    - `date_from`, `date_to`: Filter transactions within a date range.
    - `page`, `limit`: For pagination.
  - **Response Structure**: JSON array of transaction objects.
  - **Success Codes**: 200 OK
  - **Error Codes**: 404 Not Found

- **GET /budgets/{budget_id}/transactions/{transaction_id}**
  - **Description**: Retrieve details for a specific transaction.
  - **Response Structure**: A transaction object in JSON.
  - **Success Codes**: 200 OK
  - **Error Codes**: 404 Not Found

- **POST /budgets/{budget_id}/transactions**
  - **Description**: Create a new transaction in a budget category.
  - **Request Payload**:
    ```json
    {
      "category_id": "uuid",
      "amount": { "amount": 100 },
      "transaction_type": "INCOME" or "EXPENSE",
      "occurred_date": "YYYY-MM-DDTHH:MM:SSZ",
      "description": "optional description",
      "user_id": "uuid"
    }
    ```
  - **Validation Rules**:
    - Transaction currency must match the budget's currency.
    - Transaction date should fall within the budget's active period (with allowances for retroactive entries as per US-013).
  - **Response**: No content; only HTTP status code 201 Created is returned.
  - **Error Codes**: 400 Bad Request, 409 Conflict, 404 Not Found

- **PUT /budgets/{budget_id}/transactions/{transaction_id}**
  - **Description**: Update an existing transaction.
  - **Request Payload**:
    ```json
    {
      "category_id": "uuid",
      "amount": { "amount": 120 },
      "transaction_type": "INCOME" or "EXPENSE",
      "occurred_date": "YYYY-MM-DDTHH:MM:SSZ",
      "description": "updated description"
    }
    ```
  - **Response**: No content; only HTTP status code 200 OK is returned.
  - **Error Codes**: 400 Bad Request, 404 Not Found

- **DELETE /budgets/{budget_id}/transactions/{transaction_id}**
  - **Description**: Delete a transaction and update related statistics.
  - **Response**: No content; only HTTP status code 200 OK is returned.
  - **Error Codes**: 404 Not Found

### Statistics

- **GET /budgets/{budget_id}/statistics**
  - **Description**: Retrieve overall financial statistics for a budget.
  - **Response Structure**:
    ```json
    {
      "current_balance": { "amount": 0, "currency": "USD" },
      "daily_available_amount": { "amount": 0, "currency": "USD" },
      "daily_average": { "amount": 0, "currency": "USD" },
      "used_limit": { "amount": 0, "currency": "USD" },
      "categories_statistics": [ { /* details per category */ } ]
    }
    ```
  - **Success Codes**: 200 OK
  - **Error Codes**: 404 Not Found

- **GET /budgets/{budget_id}/categories/{category_id}/statistics**
  - **Description**: Retrieve statistics for a specific category within a budget.
  - **Response Structure**: A JSON object representing category-specific statistics.
  - **Success Codes**: 200 OK
  - **Error Codes**: 404 Not Found

## 3. Authentication and Authorization

- The API will utilize JWT (JSON Web Tokens) for authentication.
- Clients must include a valid Bearer token in the Authorization header (e.g., `Authorization: Bearer <token>`).
- Authorization policies will ensure that if a resource does not belong to the user, a 404 Not Found is returned.
- Additional measures, such as rate limiting, may be implemented to enhance security and performance.

## 4. Validation and Business Logic

- **Data Validation**:
  - Request payloads will be validated using schema validators (e.g., Pydantic in FastAPI).
  - Budget names (budget_name) must be between 3-100 characters.
  - Each category name must be unique within its budget and a maximum of 5 categories per budget is allowed.
  - Transaction currency must match the budget's currency.
  - Transaction dates must fall within the budget's active period (with accommodations for retroactive entries as per US-013).

- **Business Logic Implementation**:
  - The domain logic (e.g., budget renewal, transaction validations, category deletion strategies) will be handled by corresponding command handlers.
  - Logical operations (such as transferring or deleting transactions upon category deletion) will be executed according to the specified transfer_policy.
  - Automatic budget renewal (US-012) and deactivation (US-003) will be supported through both API endpoints and scheduled tasks (e.g., using Celery).

- **Error Handling**:
  - The API will perform early validation and return appropriate HTTP error codes (e.g., 400 for Bad Request, 404 for Not Found, 409 for Conflict).
  - Error messages will be clear and designed to guide the client on corrective actions.

- **Performance & Security**:
  - Endpoints returning lists will support pagination, filtering, and sorting.
  - Secure communication and proper rate limiting will be enforced to protect against abuse and ensure a reliable service.
