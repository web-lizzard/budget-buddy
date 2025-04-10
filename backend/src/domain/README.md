# Domain Module

This module encapsulates the core business logic and rules of the application, following Domain-Driven Design (DDD) principles.

## Key Concepts

*   **Aggregates, Entities, Value Objects:** Represents the core concepts and data structures of the business domain.
*   **Domain Services:** Contains domain logic that doesn't naturally fit within an entity or value object.
*   **Domain Events:** Signifies significant occurrences within the domain.
*   **Repositories (Ports):** Defines interfaces for data persistence, implemented by adapters.
*   **Ubiquitous Language:** This module strictly adheres to the Ubiquitous Language defined for the project (see `docs/mvp/ubiquitous_language.md`) to ensure clear communication and alignment between the code and business requirements.

## Responsibilities

*   Enforcing business rules and invariants.
*   Defining the structure and behavior of the core domain concepts.
*   Remaining independent of infrastructure concerns (e.g., databases, UI).
