# Action Plan: Implementacja uwierzytelniania w aplikacji FastAPI

## Przygotowanie środowiska i zależności

1. **Instalacja niezbędnych pakietów**: Zainstaluj wszystkie wymagane zależności, w tym python-jose do obsługi JWT oraz passlib do bezpiecznego hashowania haseł.
2. **Konfiguracja zmiennych środowiskowych**: Uzuepełnij plik konfiguracyjny `/backend/src/infrastructure/settings.py` zawierający ustawienia dla JWT, takie jak SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES oraz REFRESH_TOKEN_EXPIRE_DAYS.

## Przygotowanie struktury bazy danych

3. **Utworzenie tabeli users**: Zaprojektuj tabelę users zawierającą tylko niezbędne pola: id (UUID), email (unikalny), hashed_password oraz created_at. Nie dodawaj żadnych nadmiarowych pól, które nie są wymagane do procesu uwierzytelniania. Dodaj ją do `/backend/src/adapters/outbound/persistence/sql_alchemy/models.py`
4. **Relacja z istniejącymi tabelami**: Zmodyfikuj istniejące tabele, aby pole user_id stało się poprawnym kluczem obcym odnoszącym się do tabeli users, zastępując dotychczasowe statyczne UUID.

## Implementacja mechanizmów bezpieczeństwa

6. **Funkcje hashowania haseł**: Stwórz asynchroniczne wrappery dla funkcji hashowania i weryfikacji haseł, wykorzystując `run_in_threadpool` do uruchamiania blokujących operacji bcrypt w sposób asynchroniczny.
7. **Generowanie i weryfikacja JWT**: Zaimplementuj funkcje do tworzenia tokenów JWT z odpowiednimi czasami wygaśnięcia dla access i refresh tokenów. Dodaj funkcję do walidacji tokenu i ekstrakcji user_id.
8. **Zależność pobierania user_id**: Utwórz funkcję zależności FastAPI, która będzie wyodrębniać i weryfikować user_id z tokenu JWT bez konieczności odpytywania bazy danych przy każdym żądaniu.

## Implementacja endpointów uwierzytelniania w module
`/backend/src/adapters/inbound/api/routers/auth`


9. **Endpoint rejestracji**: Zaimplementuj endpoint `/register`, który przyjmuje email i hasło, sprawdza unikalność adresu email, haszuje hasło asynchronicznie i zapisuje nowego użytkownika w bazie danych.
10. **Endpoint logowania**: Utwórz endpoint `/login` akceptujący dane logowania (email i hasło), weryfikujący poświadczenia i zwracający parę tokenów: access_token i refresh_token.
11. **Endpoint odświeżania tokenów**: Dodaj endpoint `/refresh` do generowania nowego access_token na podstawie ważnego refresh_token, zapewniając ciągłość sesji użytkownika.


## Integracja z istniejącą aplikacją

13. **Aktualizacja istniejących endpointów**: Zaktualizuj wszystkie istniejące endpointy, aby używały `get_current_user_id` jako zależności, zapewniając tym samym ochronę dostępu do zasobów. `/backend/src/adapters/inbound/api/routers/budgets`
14. **Zmiana logiki biznesowej**: Zmodyfikuj kod aplikacji, aby zamiast statycznego UUID używał identyfikatora użytkownika z tokenu uwierzytelniającego do filtrowania i zarządzania danymi pobieranej z utworzonego wcześniej deps do auth.
15. **Middleware dla uwierzytelniania**: Jeśli wymagane, dodaj middleware FastAPI do obsługi globalnej walidacji tokenów oraz zarządzania wyjątkami uwierzytelniania.

## Testowanie i wdrożenie

16. **Testy jednostkowe**: Przygotuj testy jednostkowe dla kluczowych funkcji związanych z bezpieczeństwem, hashowaniem haseł i generowaniem tokenów JWT.
18. **Dokumentacja**: Zaktualizuj dokumentację API, aby odzwierciedlała nowy system uwierzytelniania, z przykładami użycia dla każdego endpointu. `/docs/api_plan.md`
