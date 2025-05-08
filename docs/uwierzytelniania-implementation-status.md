# Status implementacji modułu uwierzytelniania

## Zrealizowane kroki

1.  **Konfiguracja JWT**:
    *   Ustawienia JWT (sekret, algorytm, czasy życia tokenów) zdefiniowane w `backend/src/infrastructure/settings.py`.

2.  **Model Użytkownika i Baza Danych**:
    *   `UserModel` stworzony w `backend/src/adapters/outbound/persistence/sql_alchemy/models.py`.
    *   Zdefiniowano relacje kluczy obcych do tabeli `users` w istniejących modelach.

3.  **Podstawowe Mechanizmy Bezpieczeństwa (`backend/src/application/security.py`)**:
    *   Implementacja asynchronicznych funkcji hashowania (`get_password_hash`) i weryfikacji haseł (`verify_password`) przy użyciu `passlib`.
    *   Implementacja funkcji tworzenia tokenów JWT (`create_access_token`, `create_refresh_token`) przy użyciu `python-jose`.
        *   `create_access_token` dodaje `type: "access"` do ładunku tokenu.
        *   `create_refresh_token` dodaje `type: "refresh"` do ładunku tokenu.
    *   Implementacja funkcji `verify_token_and_extract_sub` do walidacji tokenu, ekstrakcji identyfikatora użytkownika (`sub`) oraz weryfikacji oczekiwanego typu tokenu (`expected_type`).

4.  **Zależności FastAPI dla Autoryzacji (`backend/src/adapters/inbound/api/dependencies/auth.py`)**:
    *   Stworzenie `reusable_oauth2_mandatory` (`OAuth2PasswordBearer`).
    *   Stworzenie `reusable_oauth2_optional` (`OAuth2PasswordBearer` z `auto_error=False`).
    *   Implementacja asynchronicznych funkcji zależności `get_current_user_id` (dla obowiązkowego tokenu) i `get_current_user_id_optional` (dla opcjonalnego tokenu). Obie funkcje:
        *   Pobierają token z nagłówka `Authorization`.
        *   Wykorzystują `verify_token_and_extract_sub` z `expected_type="access"` do walidacji tokenu dostępowego i uzyskania `user_id`.

5.  **Router Autoryzacji (`backend/src/adapters/inbound/api/routers/auth/router.py`)**:
    *   Implementacja endpointu `/refresh`:
        *   Przyjmuje `refresh_token`.
        *   Wykorzystuje `verify_token_and_extract_sub` z `expected_type="refresh"` do walidacji refresh tokenu.
        *   Generuje i zwraca nowy `access_token`.
    *   Endpointy `/register` i `/login`:
        *   Szkielety endpointów są zaimplementowane.
        *   Obecna logika jest tymczasowa/symulowana i oczekuje na integrację z `UserService`.

## Kolejne kroki

1.  **Implementacja `UserService`**:
    *   **Plik**: Utworzenie `backend/src/application/services/user_service.py`.
    *   **Logika**: Zdefiniowanie klasy `UserService` z metodami:
        *   `async def create_user(self, email: str, password: str)`: Walidacja danych, hashowanie hasła (użycie `get_password_hash`), symulacja sprawdzania unikalności emaila i zapisu do bazy danych, zwracanie danych użytkownika.
        *   `async def authenticate_user(self, email: str, password: str)`: Symulacja pobrania użytkownika, weryfikacja hasła (użycie `verify_password`), zwracanie danych użytkownika lub `None`.

2.  **Integracja `UserService` z Routerem Autoryzacji**:
    *   **Plik**: Modyfikacja `backend/src/adapters/inbound/api/routers/auth/router.py`.
    *   **Logika**:
        *   Dodanie zależności (dependency) dostarczającej instancję `UserService`.
        *   Zastąpienie obecnej, symulowanej logiki w endpointach `/register` i `/login` wywołaniami odpowiednich metod z `UserService`.
        *   Obsługa wyjątków i zwracanie odpowiednich odpowiedzi HTTP (w tym tokenów JWT po udanym logowaniu).

3.  **Aktualizacja Istniejących Endpointów (np. Budżety)**:
    *   **Plik**: Modyfikacja `backend/src/adapters/inbound/api/routers/budgets/base_router.py` (i potencjalnie innych routerów).
    *   **Logika**: Dodanie zależności `get_current_user_id` (lub `get_current_user_id_optional`) z `dependencies/auth.py` do endpointów wymagających autoryzacji.

4.  **Dostosowanie Logiki Biznesowej pod Kątem Uwierzytelnionego Użytkownika**:
    *   **Pliki**: Głównie routery (np. `budgets/base_router.py`) i powiązane serwisy.
    *   **Logika**: Wykorzystanie `user_id` (uzyskanego z tokenu) w logice aplikacji do operacji specyficznych dla użytkownika (na razie symulowane, np. logowanie, przekazywanie `user_id` do serwisów).

5.  **Testy Jednostkowe**:
    *   **Pliki**: Tworzenie testów w strukturze `backend/tests/`.
    *   **Logika**: Przygotowanie testów dla `UserService`, zależności autoryzacyjnych (`dependencies/auth.py`) oraz kluczowych endpointów autoryzacyjnych.

6.  **Aktualizacja Dokumentacji API**:
    *   **Plik**: Modyfikacja `/docs/api_plan.md` (lub innego wskazanego pliku).
    *   **Logika**: Zaktualizowanie opisów endpointów, dodanie informacji o wymaganej autoryzacji i przykładów użycia.
