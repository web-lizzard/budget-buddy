# Adapters Module

This module implements the Ports and Adapters (Hexagonal Architecture) pattern. It connects the application core (domain and application modules) to external systems and infrastructure.

## Structure

*   **Driving Adapters:** Handle incoming requests/interactions (e.g., REST API controllers, message queue listeners).
*   **Driven Adapters:** Implement interfaces (ports) defined in the domain or application layers to interact with external systems (e.g., database repositories, external service clients).

## Responsibilities

*   Translating external requests/data formats into application/domain commands or queries.
*   Translating application/domain results (DTOs) into external data formats.
*   Implementing infrastructure concerns (e.g., database interactions, API calls, message publishing).
*   Containing framework-specific code and dependencies.
