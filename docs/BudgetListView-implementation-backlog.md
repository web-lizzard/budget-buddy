# BudgetListView - Podsumowanie implementacji i backlog

## 1. Podsumowanie ukończonych prac

W ramach implementacji widoku listy budżetów (`BudgetListView`) zrealizowano następujące kroki zgodnie z planem `BudgetListView-view-implementation-plan.md`:

*   **Krok 1: Konfiguracja Routingu:** Utworzono stronę `pages/budgets/index.vue`, która obsługuje ścieżkę `/budgets`.
*   **Krok 2: Utworzenie Typów:** Zdefiniowano niezbędne interfejsy TypeScript dla DTO (`BudgetDTO`, `PaginatedBudgetsDTO`, etc.) oraz ViewModel (`BudgetListItemViewModel`) w pliku `types/budget.ts`.
*   **Krok 3: Utworzenie Store'u Pinia:** Stworzono store `stores/budgetStore.ts` używając składni `setup function`. Zaimplementowano stan (`ref`), akcje (`fetchBudgets`, `setFilter`, `setPage`, `setItemsPerPage`, `setSort`) oraz podstawową logikę komunikacji z API (`$fetch`) i obsługę błędów. Zrefaktoryzowano zgodnie z feedbackiem.
*   **Krok 4: Implementacja Funkcji Mapującej:** Udoskonalono funkcję `mapBudgetDTOToViewModel` w store do poprawnego obliczania statusu budżetu i przygotowania danych dla widoku.
*   **Krok 5: Rozwinięcie Komponentu `BudgetListView`:** Zintegrowano stronę `pages/budgets/index.vue` ze storem Pinia (`storeToRefs`), dodano obsługę stanów ładowania i błędów oraz przygotowano strukturę do integracji komponentów podrzędnych.
*   **Krok 6: Utworzenie Komponentu `BudgetFilterTabs`:** Zaimplementowano komponent `components/BudgetFilterTabs.vue` z użyciem `shadcn/vue Tabs`, obsługujący `v-model` do filtrowania.
*   **Krok 7: Utworzenie Komponentu `CreateBudgetButton`:** Zaimplementowano komponent `components/CreateBudgetButton.vue` z użyciem `shadcn/vue Button`, emitujący zdarzenie `click`.
*   **Krok 8: Utworzenie Komponentu `BudgetListTable`:** Zaimplementowano komponent `components/BudgetListTable.vue` z użyciem `shadcn/vue Table`, `Skeleton`. Dodano obsługę:
    *   Wyświetlania danych z propsów.
    *   Stanu ładowania (Skeleton).
    *   Pustego stanu (`TableCaption`).
    *   Paginacji (uproszczonej, za pomocą `Button`).
    *   Sortowania (klikalne nagłówki ze wskaźnikami - ikony `lucide-vue-next`).
    *   Formatowania danych (daty, waluty) przy użyciu `Intl`.
    *   Emitowania zdarzeń (`update:pagination`, `update:sorting`, `row-click`).
*   **Krok 9: Integracja Komponentów w `BudgetListView`:** Zintegrowano wszystkie komponenty podrzędne (`BudgetFilterTabs`, `CreateBudgetButton`, `BudgetListTable`) w `pages/budgets/index.vue`, przekazując propsy i obsługując zdarzenia.
*   **Implementacja Nawigacji:** Dodano nawigację do szczegółów budżetu po kliknięciu wiersza (`handleRowClick` w `pages/budgets/index.vue` używając `useRouter`). Pominięto nawigację przycisku tworzenia zgodnie z ustaleniami.
*   **Poprawki Lintera:** Rozwiązano większość zgłoszonych problemów lintera (poza tymi związanymi z nierozpoznawaniem aliasów `@/` przez lintera w niektórych przypadkach).

## 2. Zaległości implementacyjne (Backlog)

Aby w pełni zakończyć implementację zgodnie z pierwotnym planem i najlepszymi praktykami, pozostały następujące zadania:

*   **Nawigacja "Utwórz Budżet":** Zaimplementować logikę po kliknięciu przycisku "Utwórz Budżet" (obecnie pominięte na życzenie - planowany modal).
*   **API Endpoint:** Potwierdzić i ewentualnie skonfigurować (np. przez zmienne środowiskowe) rzeczywisty adres URL endpointu API w `stores/budgetStore.ts` (obecnie: `/api/budgets`).
*   **Obsługa błędów API:** Rozbudować obsługę błędów w store (`catch` w `fetchBudgets`), aby lepiej reagować na różne statusy odpowiedzi API (np. 401, 403, 404).
*   **Autentykacja:** Dodać obsługę przekazywania tokenów autentykacyjnych w zapytaniach do API (np. w nagłówkach `$fetch`).
*   **Zaawansowana Paginacja (Opcjonalnie):** Rozważyć implementację pełnego komponentu paginacji `shadcn/vue`, jeśli uproszczone przyciski okażą się niewystarczające (wymaga dalszego zbadania poprawnej struktury komponentów `shadcn/vue Pagination`).
*   **Wybór Liczby Elementów na Stronę:** Dodać możliwość zmiany `itemsPerPage` przez użytkownika (np. za pomocą komponentu `Select`).
*   **Formatowanie Walut/Dat:** Upewnić się, że formatowanie walut i dat (`Intl`) używa odpowiednich ustawień regionalnych (locale), potencjalnie konfigurowalnych.
*   **Tłumaczenia (i18n):** Przystosować wszystkie teksty widoczne dla użytkownika (etykiety, komunikaty) do internacjonalizacji (np. używając modułu `@nuxtjs/i18n`).
*   **Styling i Dostępność (Krok 10):** Dokładne przejrzenie i dopracowanie stylów oraz atrybutów ARIA dla lepszej dostępności.
*   **Testowanie (Krok 11):** Dodanie testów jednostkowych (np. dla logiki store'u, funkcji pomocniczych) i/lub testów komponentów (Vitest, Vue Testing Library), jeśli zostaną uznane za potrzebne.
*   **Optymalizacja:** Przeanalizować wydajność, zwłaszcza przy dużej liczbie budżetów (np. debouncing filtrów/wyszukiwania, optymalizacja renderowania tabeli).

## 3. Sugestie dotyczące refaktoryzacji

Chociaż obecna implementacja jest zgodna z planem, można rozważyć następujące refaktoryzacje w przyszłości dla lepszej organizacji i reużywalności:

*   **Funkcje Pomocnicze:** Wydzielić funkcje formatujące (`formatDateRange`, `formatCurrency`, `parseLimitString`) oraz funkcję mapującą (`mapBudgetDTOToViewModel`) do dedykowanych plików w katalogu `utils/` (np. `utils/formatters.ts`, `utils/mappers.ts`).
*   **Composable `useBudgets`:** Jeśli logika w komponencie `pages/budgets/index.vue` stanie się bardziej złożona (np. dodatkowe filtry, wyszukiwanie), można wydzielić interakcję ze storem Pinia do dedykowanego composable `useBudgets.ts`, który udostępniałby potrzebny stan i funkcje obsługi zdarzeń.
*   **Typy API:** Jeśli typy DTO (np. `BudgetDTO`, `PaginatedBudgetsDTO`) są używane w wielu miejscach (np. również po stronie serwera lub w innych modułach frontendu), rozważyć ich wydzielenie do współdzielonej biblioteki/pakietu.
*   **Konfiguracja Tabeli:** Definicję kolumn (`columns`) w `BudgetListTable.vue` można by potencjalnie uczynić bardziej konfigurowalną lub dynamiczną, jeśli tabela miałaby być reużywana w innych kontekstach z różnymi zestawami kolumn.
