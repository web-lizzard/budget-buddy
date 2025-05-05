# Podsumowanie Implementacji i Backlog: Aktualizacja Rekordu Statystyk po Edycji Transakcji

Ten dokument podsumowuje zmiany wprowadzone w celu obsługi aktualizacji rekordów statystyk (`StatisticsRecord`) po edycji transakcji (`TransactionUpdated` event) oraz przedstawia backlog zadań pozostałych do wykonania.

## Wykonane Kroki

1.  **Modyfikacja Domeny i Persystencji dla Powiązania `StatisticsRecord` <-> `Transaction`:**
    *   **Agregat Domeny:** Dodano opcjonalne pole `transaction_id: uuid.UUID | None` do `StatisticsRecord` (`backend/src/domain/aggregates/statistics_record.py`).
    *   **Model SQLAlchemy:** Dodano kolumnę `transaction_id: Mapped[uuid.UUID | None]` do `StatisticsRecordModel` (`backend/src/adapters/outbound/persistence/sql_alchemy/models.py`), w tym klucz obcy (FK) do `transactions.id` z `ondelete="SET NULL"`, indeks oraz ograniczenie unikalności.
    *   **Komenda:** Dodano pole `transaction_id: uuid.UUID` do `CalculateStatisticsCommand` (`backend/src/application/commands/calculate_statistics_command.py`).
    *   **Subskrybent (`TransactionAdded`):** Zaktualizowano `transaction_added_subscriber.py`, aby pobierał `transaction_id` ze zdarzenia `TransactionAdded` i przekazywał je do `CalculateStatisticsCommand`.
    *   **Fabryka:** Stworzono `StatisticsRecordUpdateFactory` (`backend/src/domain/factories/statistics_record_update_factory.py`) do aktualizacji rekordu `StatisticsRecord` przy ponownym przeliczaniu jego wartości.
    *   **Handler (`CalculateStatistics`):** Zaktualizowano `CalculateStatisticsCommandHandler`, aby wstrzykiwał i używał `StatisticsRecordUpdateFactory` do aktualizacji rekordu, przekazując `transaction_id` z komendy.

2.  **Dodanie Nowych Metod do Repozytoriów:**
    *   **Interfejs `StatisticsRepository`:** Zdefiniowano metodę `find_by_transaction_id(self, transaction_id: uuid.UUID, user_id: uuid.UUID) -> StatisticsRecord` w `backend/src/domain/ports/outbound/statistics_repository.py`.
    *   **Implementacja `SQLAlchemyStatisticsRepository`:** Zaimplementowano metodę `find_by_transaction_id` w `backend/src/adapters/outbound/persistence/sql_alchemy/repositories/statistics_repository.py`.
    *   **Interfejs `TransactionRepository`:** Zdefiniowano metodę `find_by_budget_id_and_date_range(self, budget_id: UUID, user_id: UUID, end_date: datetime) -> list[Transaction]` w `backend/src/domain/ports/transaction_repository.py`.
    *   **Implementacja `SQLAlchemyTransactionRepository`:** Zaimplementowano metodę `find_by_budget_id_and_date_range` w `backend/src/adapters/outbound/persistence/sql_alchemy/repositories/transaction_repository.py`.

## Backlog Pozostałych Zadań

Poniższe kroki należy wykonać, aby dokończyć implementację funkcjonalności:

1.  **Stworzenie Nowego Subskrybenta (`TransactionUpdated`):**
    *   **Plik do utworzenia:** `backend/src/adapters/inbound/subscribers/transaction_updated_subscriber.py`
    *   **Zadanie:**
        *   Zaimplementować funkcję `on_transaction_updated_message(message: aio_pika.IncomingMessage, ...)`.
        *   Subskrybować kolejkę `statistics_queue` z kluczem routingu `TransactionUpdated`.
        *   Deserializować wiadomość do obiektu zdarzenia `TransactionUpdated`.
        *   Wyodrębnić `transaction_id`, `budget_id`, `user_id` oraz **nową** datę transakcji (`date` lub `occurred_date` - do weryfikacji w definicji zdarzenia `TransactionUpdated`).
        *   Wysłać (dispatch) nową komendę `RecalculateStatisticsAfterUpdateCommand` (patrz Krok 4) z wyodrębnionymi danymi.
        *   Zaimplementować obsługę błędów (np. `ValidationError`, ogólne wyjątki, NACK/requeue).
    *   **Rejestracja:** Zarejestrować nowego subskrybenta w logice startowej aplikacji (np. w `backend/src/main.py` lub podobnym miejscu, gdzie konfigurowane są subskrybenci RabbitMQ).

2.  **Zdefiniowanie Nowej Komendy (`RecalculateStatisticsAfterUpdateCommand`):**
    *   **Plik do utworzenia/modyfikacji:** `backend/src/application/commands/statistics_commands.py` (lub inny plik grupujący komendy, jeśli istnieje).
    *   **Zadanie:** Zdefiniować `dataclass RecalculateStatisticsAfterUpdateCommand(Command)` zawierającą pola:
        *   `transaction_id: uuid.UUID`
        *   `budget_id: uuid.UUID`
        *   `user_id: uuid.UUID`
        *   `transaction_occurred_date: datetime` (lub odpowiednia nazwa dla daty zaktualizowanej transakcji).

3.  **Stworzenie Nowego Command Handlera (`RecalculateStatisticsAfterUpdateCommandHandler`):**
    *   **Plik do utworzenia:** `backend/src/application/commands/handlers/recalculate_statistics_after_update_command_handler.py`
    *   **Zadanie:**
        *   Zdefiniować klasę `RecalculateStatisticsAfterUpdateCommandHandler(CommandHandler[RecalculateStatisticsAfterUpdateCommand])`.
        *   Wstrzyknąć zależności w `__init__`: `UnitOfWork`, `BudgetRepository`, `TransactionRepository`, `StatisticsRepository`, `StatisticsCalculationService`, `StatisticsRecordFactory`, `Clock`.
        *   Zaimplementować metodę `async def _handle(self, command: RecalculateStatisticsAfterUpdateCommand)`:
            *   Pobrać **konkretny** rekord statystyk do aktualizacji używając `_statistics_repository.find_by_transaction_id(command.transaction_id, command.user_id)`.
            *   Pobrać budżet używając `_budget_repository.find_by(command.budget_id, command.user_id)`.
            *   Pobrać **wszystkie** transakcje dla danego budżetu **do daty wystąpienia edytowanej transakcji (włącznie)** używając `_transaction_repository.find_by_budget_id_and_date_range(budget_id=command.budget_id, user_id=command.user_id, end_date=command.transaction_occurred_date)`.
            *   Przeliczyć wartości statystyk używając `_statistics_calculation_service.calculate_statistics(budget=budget, transactions=transactions)` (zwróci obiekt/słownik z nowymi wartościami).
            *   **Zaktualizować pola** w **pobranym wcześniej** obiekcie domenowym `statistics_record` nowymi wartościami (np. `current_balance`, `daily_average`, etc.). Można również zaktualizować pole `updated_at` lub `creation_date` w zależności od logiki domenowej.
            *   Zapisać **zaktualizowany** obiekt `statistics_record` używając `_statistics_repository.save(statistics_record)` (upewnić się, że `save` obsługuje aktualizacje, np. przez `session.merge`).
            *   Zwrócić odpowiednie zdarzenie domenowe, np. `StatisticsRecalculated`, używając wstrzykniętego `Clock`.
    *   **Rejestracja:** Zarejestrować nowy handler w kontenerze DI (np. `backend/src/infrastructure/container/main_container.py`) i zmapować `RecalculateStatisticsAfterUpdateCommand` do tego handlera.

4.  **Testowanie:**
    *   **Pliki:** W katalogu `backend/tests/` (np. `application/commands/handlers/`, `adapters/inbound/subscribers/`, `integration/`).
    *   **Zadanie:**
        *   Dodać testy jednostkowe dla `RecalculateStatisticsAfterUpdateCommandHandler`.
        *   Dodać testy jednostkowe dla nowych metod w repozytoriach (choć częściowo pokryte przez testy handlera).
        *   Dodać testy integracyjne symulujące wysłanie zdarzenia `TransactionUpdated` i weryfikujące, czy odpowiedni `StatisticsRecord` został znaleziony i zaktualizowany poprawnymi wartościami (obliczonymi na podstawie transakcji do daty edytowanej transakcji).

5.  **Standardy Kodowania i Dokumentacja:**
    *   **Pliki:** Wszystkie zmodyfikowane i utworzone pliki.
    *   **Zadanie:**
        *   Przejrzeć kod pod kątem zgodności z PEP 8, użycia type hints, logowania.
        *   Zaktualizować istniejącą dokumentację (np. `README.md`, `CHANGELOG.md` w `docs/`) jeśli implementacja wprowadza istotne zmiany dla użytkownika lub dewelopera.

6.  **Integracja Fabryki:** W implementacji nowego Command Handlera `RecalculateStatisticsAfterUpdateCommandHandler` zastosować `StatisticsRecordUpdateFactory` do przeliczenia statystyk na podstawie edytowanej transakcji oraz aktualizacji odpowiednich pól w rekordzie `StatisticsRecord`.
