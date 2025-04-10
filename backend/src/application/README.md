# Application Module

This module orchestrates the application's use cases and acts as an intermediary between the domain and adapters.

## Key Concepts

*   **Application Services:** Contain the logic for specific use cases (commands and queries).
*   **Commands:** Represent actions that intend to change the system state.
*   **Queries:** Represent requests for information without altering the system state.
*   **Data Transfer Objects (DTOs):** Used for transferring data between layers (e.g., from adapters to application services, and from application services back to adapters).
*   **Ports (Interfaces):** Define contracts for driven adapters (e.g., repository interfaces if not defined in the domain).

## Responsibilities

*   Coordinating the execution of use cases by interacting with domain objects and repositories.
*   Implementing a simplified CQRS pattern:
    *   Commands and Queries use the same database.
    *   Both Commands and Queries return DTOs.
*   Handling transaction management (only in commands).
*   Mapping between input/output DTOs and domain objects.
