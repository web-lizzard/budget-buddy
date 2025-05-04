# Action Plan – Timezone Aware Refactoring

## 1. Utworzenie nowego portu "Clock"
- Utwórz plik `/src/domain/ports/clock.py`.
- Implementacja portu powinna zwracać bieżący czas jako obiekt `datetime` tz-aware (np. przy użyciu `datetime.now(timezone.utc)` z modułu `zoneinfo`). `src/adapters/outbound/clock/time_aware_clock.py`
- Zapewnij możliwość wstrzykiwania zależności (dependency injection), co umożliwi łatwe mockowanie w testach.
- Wstrzykuj odpowiednią wartość do `/src/infrastructure/container/domain_container.py`

## 2. Refaktoryzacja fabryk (Factories)
- **Pliki:**
  - `/src/domain/factories/transaction_factory.py`
  - `/src/domain/factories/budget_factory.py`
- Zastąp wszystkie bezpośrednie wywołania `datetime.now()` wywołaniami funkcji z portu "Clock".
- Wstrzykuj port "Clock" przez konstruktor lub jako argument funkcji, by umożliwić późniejsze mockowanie podczas testów.

## 3. Refaktoryzacja strategii (Strategies)
- **Pliki:**
  - Katalog `/src/domain/strategies/budget_strategy/` oraz inne pliki w katalogu `/src/domain/strategies`
- Znajdź wszystkie wywołania `datetime.now()` i zastąp je wywołaniami funkcji z portu "Clock".
- Upewnij się, że wszystkie operacje na datach (wyliczenia, porównania) są wykonywane na obiektach tz-aware.

## 4. Aktualizacja logiki domenowej
- **Pliki:**
  - `/src/domain/aggregates/budget.py`
  - `/src/domain/entities/category.py`
  - `/src/domain/aggregates/transaction.py`
- Przejrzyj wszelkie wywołania `datetime.now()` oraz porównania dat, aby upewnić się, że operacje te działają na obiektach z informacją o strefie czasowej.

## 5. Aktualizacja modeli bazy danych
- **Plik:**
  - `/src/adapters/outbound/persistence/sql_alchemy/models.py`
- Zmodyfikuj definicje kolumn typu `DateTime` tak, aby używały `DateTime(timezone=True)`.
- Przygotuj migrację destrukcyjną (ze względu na etap developmentu) do aktualizacji schematu bazy danych.

## 6. Dostosowanie testów
- **Lokalizacja:** Prawdopodobnie katalog z testami, np. `/backend/tests`.
- Zaktualizuj testy jednostkowe i integracyjne, aby weryfikowały, że generowane daty są tz-aware.
- Upewnij się, że port "Clock" jest poprawnie wstrzykiwany i może być mockowany w testach, aby symulować różne strefy czasowe i daty.
- Przejrzyj testy dotyczące porównania dat pod kątem obsługi obiektów z informacją o strefie czasowej.

## 7. Dokumentacja i finalne kroki
- Zaktualizuj dokumentację backendu dotyczącą sposobu generowania dat oraz działania portu "Clock".
- Upewnij się, że notatki developerskie (np. w tym pliku) zawierają odniesienia do konkretnych plików, które zostały zmodyfikowane.
- Przeprowadź manualne i automatyczne testy całego systemu, aby potwierdzić, że wprowadzone zmiany nie powodują regresji w działaniu aplikacji.

Podsumowując, plan działania obejmuje modyfikacje w następujących obszarach:
Utworzenie nowego portu "Clock" (/src/domain/ports/clock.py)
Modyfikacja fabryk: /src/domain/factories/transaction_factory.py, /src/domain/factories/budget_factory.py
Refaktoryzacja strategii w /src/domain/strategies (szczególnie w podfolderze budget_strategy)
Dostosowanie logiki domenowej w /src/domain/aggregates/budget.py (oraz ewentualnie w innych agregatach)
Aktualizacja modeli bazy danych w /src/adapters/outbound/persistence/sql_alchemy/models.py
Dostosowanie testów w zależności od ich lokalizacji (np. /backend/tests)
Każdy z tych kroków powinien być wdrażany etapowo, wraz z pisaniem odpowiednich testów, aby zapewnić działanie systemu z datami tz-aware na backendzie.
