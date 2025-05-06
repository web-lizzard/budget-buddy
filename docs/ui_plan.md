# Architektura UI dla Budget Buddy

## 1. Przegląd struktury UI

Architektura UI dla aplikacji Budget Buddy została zaprojektowana w celu zapewnienia intuicyjnego i wydajnego zarządzania budżetami osobistymi. Opiera się na stosie technologicznym Nuxt.js (Vue 3), Pinia do zarządzania stanem UI i logiki pomocniczej (np. polling), Nuxt Query do zarządzania stanem serwera (pobieranie, cache'owanie danych), Axios do mutacji API (POST/PUT/DELETE), Shadcn UI i Tailwind CSS do budowy interfejsu oraz Zod do walidacji danych.

Aplikacja wykorzystuje nawigację w postaci paska bocznego po lewej stronie oraz główny obszar treści po prawej. Domyślnym motywem jest ciemny. Priorytetem jest responsywność (mobile, tablet, desktop) oraz zgodność z wytycznymi dostępności (WCAG). Stany ładowania są sygnalizowane za pomocą komponentów typu Skeleton i Spinner, a błędy API komunikowane są użytkownikowi poprzez Toasty.

## 2. Lista widoków

Poniżej znajduje się lista głównych widoków oraz kluczowych modali/komponentów interaktywnych:

---

### Widok: Lista Budżetów

*   **Nazwa widoku:** `BudgetListView`
*   **Ścieżka widoku:** `/budgets`
*   **Główny cel:** Wyświetlenie listy budżetów użytkownika (aktywnych/zakończonych), umożliwienie nawigacji do szczegółów budżetu oraz inicjacja tworzenia nowego budżetu. (Realizuje US-002)
*   **Kluczowe informacje do wyświetlenia:** Nazwa budżetu, Status (Aktywny/Zakończony), Data rozpoczęcia/zakończenia, Limit całkowity, Waluta, Postęp wykorzystania limitu (opcjonalnie).
*   **Kluczowe komponenty widoku:**
    *   `DataTable` (opakowujący `Shadcn Table`): Wyświetla budżety, obsługuje paginację, sortowanie (domyślnie po dacie rozpoczęcia malejąco), stany ładowania (Skeleton) i pusty stan.
    *   `Shadcn Button`: Przycisk "Utwórz budżet" uruchamiający modal.
    *   Filtry (np. `Shadcn Tabs` lub `Select`): Do filtrowania wg statusu 'aktywny'/'zakończony'.
*   **UX, dostępność i względy bezpieczeństwa:**
    *   **UX:** Paginacja zapobiega ładowaniu zbyt wielu danych naraz. Wyraźny przycisk akcji (CTA) do tworzenia budżetu. Informacja o pustym stanie, gdy brak budżetów. Wiersze tabeli klikalne, prowadzące do szczegółów.
    *   **Dostępność:** Tabela z poprawną semantyką (`<thead>`, `<tbody>`, `scope`). Linki/przyciski z wyraźnymi etykietami, fokusowane. Paginacja obsługiwana z klawiatury.
    *   **Bezpieczeństwo:** Dane pobierane dla zalogowanego użytkownika (obsługa po stronie API/backendu).

---

### Widok: Szczegóły Budżetu

*   **Nazwa widoku:** `BudgetDetailView`
*   **Ścieżka widoku:** `/budgets/{budget_id}`
*   **Główny cel:** Wyświetlenie kompleksowych informacji o pojedynczym budżecie, w tym statystyk, ostatnich transakcji, listy kategorii oraz umożliwienie zarządzania kategoriami i transakcjami. (Realizuje częściowo US-003, US-005, US-006, US-007, US-010)
*   **Kluczowe informacje do wyświetlenia:** Nazwa budżetu, Daty, Limit całkowity, Statystyki ogólne (Saldo bieżące, Dostępna kwota dzienna, Średnia dzienna, Wykorzystany limit - z `GET /statistics`), Lista kategorii (Nazwa, Limit, Wykorzystanie - z `GET /budgets/{id}` i `GET /statistics`), Statystyki per kategoria, Wykres kołowy wydatków per kategoria, Tabela z ostatnimi 3 transakcjami (z `GET /transactions`).
*   **Kluczowe komponenty widoku:**
    *   Sekcja Statystyk (`StatsCard`): Wyświetla kluczowe metryki liczbowe.
    *   `LimitProgressBar` (opakowujący `Shadcn Progress`): Paski postępu dla limitu ogólnego i limitów kategorii, ze zmianą koloru (>80%) i ikoną ostrzegawczą.
    *   `CategorySpendingChart` (opakowujący bibliotekę wykresów): Wykres kołowy udziału wydatków w kategoriach.
    *   Tabela Ostatnich Transakcji (`Shadcn Table`): Wyświetla 3 ostatnie transakcje.
    *   Lista Kategorii (np. `Shadcn Card` lub `Accordion`): Wyświetla nazwy kategorii, limity, postęp wykorzystania.
    *   Przyciski Akcji (`Shadcn Button`): "Dodaj transakcję", "Zobacz wszystkie transakcje", "Dezaktywuj budżet", "Edytuj kategorię" (przy każdej), "Usuń kategorię" (przy każdej, uruchamia modal z wyborem polityki).
    *   `Skeleton Loader`: Dla sekcji ładowanych asynchronicznie.
*   **UX, dostępność i względy bezpieczeństwa:**
    *   **UX:** Przejrzysty układ informacji. Wizualizacja danych (wykres, paski postępu) ułatwia szybką ocenę sytuacji. Łatwy dostęp do kluczowych akcji (dodawanie transakcji, zarządzanie kategoriami). Mechanizm pollingu statystyk zapewnia aktualizację danych po dodaniu transakcji.
    *   **Dostępność:** Poprawna struktura nagłówków. Elementy interaktywne (przyciski, linki) z etykietami, fokusowane. Wykres z alternatywnym opisem tekstowym. Paski postępu z atrybutami ARIA (`aria-valuenow`, etc.).
    *   **Bezpieczeństwo:** Widok dostępny tylko dla właściciela budżetu (kontrola API).

---

### Widok: Lista Transakcji

*   **Nazwa widoku:** `TransactionListView`
*   **Ścieżka widoku:** `/budgets/{budget_id}/transactions`
*   **Główny cel:** Wyświetlenie pełnej listy transakcji dla danego budżetu z możliwością edycji i usuwania. (Realizuje częściowo US-008, US-009)
*   **Kluczowe informacje do wyświetlenia:** Data transakcji, Opis, Kategoria, Kwota, Typ (Wydatek/Przychód).
*   **Kluczowe komponenty widoku:**
    *   Tabela Transakcji (`Shadcn Table`): Wyświetla transakcje.
    *   Mechanizm Infinite Scroll: Automatyczne ładowanie kolejnych stron przy przewijaniu (Intersection Observer + Nuxt Query `useInfiniteQuery`).
    *   `Shadcn Spinner`: Wskaźnik ładowania kolejnych transakcji.
    *   Przyciski Akcji (`Shadcn Button`): "Edytuj transakcję", "Usuń transakcję" (przy każdej transakcji, uruchamia modal potwierdzający).
    *   Filtry (opcjonalnie w przyszłości): np. wg daty, kategorii.
    *   Komunikat o pustym stanie.
*   **UX, dostępność i względy bezpieczeństwa:**
    *   **UX:** Infinite scroll zapewnia płynne przeglądanie długiej listy transakcji bez przeładowywania strony. Wskaźnik ładowania informuje o pobieraniu danych.
    *   **Dostępność:** Elementy listy/wiersze tabeli z poprawną semantyką. Przyciski akcji dostępne z klawiatury.
    *   **Bezpieczeństwo:** Dostęp do listy transakcji tylko dla właściciela budżetu.

---

### Modal: Tworzenie Budżetu

*   **Nazwa komponentu:** `CreateBudgetModal`
*   **Cel:** Umożliwienie użytkownikowi stworzenia nowego budżetu wraz z początkowymi kategoriami. (Realizuje US-001, US-004)
*   **Kluczowe informacje/pola:** Nazwa budżetu, Limit całkowity, Waluta, Data rozpoczęcia, Data zakończenia, Strategia (uproszczona lub domyślna dla MVP), Dynamiczna sekcja dodawania kategorii (Nazwa, Limit).
*   **Kluczowe komponenty:**
    *   `Shadcn Dialog`: Kontener modala.
    *   `BudgetForm.vue` (wykorzystujący `vee-validate` + `Zod`): Formularz z polami (`Shadcn Input`, `Select`, `Calendar`), dynamicznym dodawaniem/usuwaniem pól kategorii (max 5), walidacją w czasie rzeczywistym (unikalność nazw kat., suma limitów kat. <= limit budżetu).
    *   Komunikaty walidacyjne przy polach oraz dedykowany obszar na błędy dotyczące sekcji kategorii.
    *   Przycisk "Zapisz".
*   **UX, dostępność i względy bezpieczeństwa:**
    *   **UX:** Płynne dodawanie kategorii. Natychmiastowa informacja zwrotna o błędach walidacji. Logika formularza zamknięta w composable/store Pinia.
    *   **Dostępność:** Poprawne etykiety pól, zarządzanie focusem wewnątrz modala, obsługa z klawiatury.
    *   **Bezpieczeństwo:** Walidacja po stronie klienta i serwera (API).

---

### Modal: Tworzenie/Edycja Transakcji

*   **Nazwa komponentu:** `AddEditTransactionModal`
*   **Cel:** Dodanie nowej lub modyfikacja istniejącej transakcji. (Realizuje US-007, US-008)
*   **Kluczowe informacje/pola:** Kategoria (wybór z listy), Kwota, Typ (Wydatek/Przychód), Data i czas wystąpienia, Opis (opcjonalny). Waluta dziedziczona z budżetu (tylko do wyświetlenia).
*   **Kluczowe komponenty:**
    *   `Shadcn Dialog`.
    *   `TransactionForm.vue` (`vee-validate` + `Zod`): Formularz z polami (`Shadcn Select`, `Input`, `Calendar`, `Radio Group`).
    *   Komunikaty walidacyjne.
    *   Przycisk "Zapisz".
*   **UX, dostępność i względy bezpieczeństwa:**
    *   **UX:** Prosty i szybki sposób na dodawanie/edycję transakcji. Wybór kategorii z predefiniowanej listy.
    *   **Dostępność:** Etykiety, focus management, obsługa z klawiatury.
    *   **Bezpieczeństwo:** Walidacja danych. Transakcja przypisana do budżetu użytkownika.

---

### Modal: Edycja/Dodanie Kategorii

*   **Nazwa komponentu:** `EditCategoryModal`
*   **Cel:** Zmiana nazwy i limitu istniejącej kategorii. (Realizuje US-005)
*   **Kluczowe informacje/pola:** Nazwa kategorii, Limit kategorii.
*   **Kluczowe komponenty:**
    *   `Shadcn Dialog`.
    *   `CategoryForm.vue` (`vee-validate` + `Zod`): Formularz z polami (`Shadcn Input`).
    *   Komunikaty walidacyjne (np. unikalność nowej nazwy w obrębie budżetu).
    *   Przycisk "Zapisz".
*   **UX, dostępność i względy bezpieczeństwa:**
    *   **UX:** Szybka edycja bez opuszczania widoku szczegółów budżetu.
    *   **Dostępność:** Etykiety, focus management, obsługa z klawiatury.
    *   **Bezpieczeństwo:** Walidacja danych. Edycja tylko dla właściciela budżetu.

---

### Modal: Potwierdzenie Usunięcia (Kategorii/Transakcji)

*   **Nazwa komponentu:** `ConfirmDeleteDialog`
*   **Cel:** Potwierdzenie przez użytkownika operacji usunięcia, z opcjonalnym wyborem strategii (dla kategorii). (Realizuje częściowo US-006, US-009)
*   **Kluczowe informacje/pola:** Komunikat potwierdzający. Dla usuwania kategorii: Opcje polityki (`Shadcn Radio Group`: "Usuń powiązane transakcje" / "Przenieś transakcje do innej kategorii"). Jeśli "Przenieś" wybrane: `Shadcn Select` z listą pozostałych kategorii docelowych.
*   **Kluczowe komponenty:**
    *   `Shadcn Dialog`.
    *   Tekst potwierdzenia.
    *   Elementy wyboru polityki (dla kategorii).
    *   Przyciski "Potwierdź" / "Anuluj".
*   **UX, dostępność i względy bezpieczeństwa:**
    *   **UX:** Zapobiega przypadkowemu usunięciu danych. Jasno komunikuje konsekwencje (dla kategorii).
    *   **Dostępność:** Dialog modalny z zarządzaniem focusem. Przyciski i opcje wyboru dostępne z klawiatury.
    *   **Bezpieczeństwo:** Operacja wykonywana po potwierdzeniu.

---

## 3. Mapa podróży użytkownika

Główny przepływ użytkownika obejmuje tworzenie budżetu, dodawanie transakcji i obserwowanie statystyk:

1.  **Start:** Użytkownik loguje się (pomijane w MVP) i trafia do widoku `BudgetListView` (`/budgets`).
2.  **Tworzenie Budżetu:**
    *   Klika przycisk "Utwórz budżet".
    *   Pojawia się `CreateBudgetModal`.
    *   Wypełnia formularz (`BudgetForm.vue`), dodając kategorie i limity. Otrzymuje walidację w czasie rzeczywistym.
    *   Klika "Zapisz". Modal wysyła `POST /budgets`.
    *   Po sukcesie: Modal znika, `BudgetListView` odświeża się (invalidacja Nuxt Query), pojawia się toast sukcesu.
3.  **Nawigacja do Szczegółów:**
    *   Klika na nowo utworzony budżet w tabeli `BudgetListView`.
    *   Przechodzi do `BudgetDetailView` (`/budgets/{id}`).
4.  **Przeglądanie Szczegółów:**
    *   Widok ładuje dane (`GET /budgets/{id}`, `GET /statistics`). Wyświetlane są informacje o budżecie, puste statystyki, lista kategorii.
5.  **Dodawanie Transakcji:**
    *   Klika przycisk "Dodaj transakcję".
    *   Pojawia się `AddEditTransactionModal`.
    *   Wypełnia formularz (`TransactionForm.vue`).
    *   Klika "Zapisz". Modal wysyła `POST /budgets/{id}/transactions`.
    *   Po sukcesie: Modal znika, pojawia się toast sukcesu. Lista ostatnich transakcji w `BudgetDetailView` odświeża się (invalidacja Nuxt Query). Uruchamiany jest mechanizm pollingu statystyk (Pinia store).
6.  **Obserwacja Statystyk:**
    *   Pinia store cyklicznie odpytuje `GET /statistics` (z exponential backoff) poprzez Nuxt Query.
    *   Gdy API zwróci zaktualizowane statystyki, Nuxt Query automatycznie odświeża dane w `BudgetDetailView`.
    *   Użytkownik widzi zaktualizowane saldo, wykorzystanie limitów (paski postępu, wykres).
7.  **(Opcjonalnie) Przeglądanie Wszystkich Transakcji:**
    *   Klika "Zobacz wszystkie transakcje" w `BudgetDetailView`.
    *   Przechodzi do `TransactionListView` (`/budgets/{id}/transactions`).
    *   Widzi dodaną transakcję. Może przewijać listę (infinite scroll).

Inne przepływy obejmują edycję/usuwanie kategorii i transakcji, aktywowane przez odpowiednie przyciski w `BudgetDetailView` lub `TransactionListView`, prowadzące przez odpowiednie modale (`EditCategoryModal`, `AddEditTransactionModal`, `ConfirmDeleteDialog`).

## 4. Układ i struktura nawigacji

*   **Główny Układ (`AppLayout.vue`):**
    *   Pasek boczny (`SidebarNav.vue`) po lewej stronie, zawierający główne linki nawigacyjne (na razie tylko "Budżety" -> `/budgets`).
    *   Główny obszar treści (`<NuxtPage />`) po prawej stronie, gdzie renderowane są poszczególne widoki (`BudgetListView`, `BudgetDetailView`, `TransactionListView`).
*   **Nawigacja:**
    *   **Podstawowa:** Poprzez kliknięcie linków w pasku bocznym.
    *   **Kontekstowa:**
        *   Kliknięcie wiersza budżetu w `BudgetListView` -> nawigacja do `BudgetDetailView`.
        *   Kliknięcie przycisku "Zobacz wszystkie transakcje" w `BudgetDetailView` -> nawigacja do `TransactionListView`.
    *   **Akcje w miejscu:** Kliknięcie przycisków "Utwórz budżet", "Dodaj transakcję", "Edytuj/Usuń Kategorię/Transakcję" otwiera odpowiednie modale (`Shadcn Dialog`) bez zmiany widoku.

## 5. Kluczowe komponenty reużywalne

Oprócz komponentów z biblioteki Shadcn UI, planuje się stworzenie następujących kluczowych komponentów reużywalnych:

*   **`AppLayout.vue`:** Definiuje główną strukturę strony z paskiem bocznym i obszarem treści.
*   **`SidebarNav.vue`:** Komponent paska bocznego z linkami nawigacyjnymi.
*   **`DataTable.vue`:** Opakowanie na `Shadcn Table` obsługujące paginację, sortowanie, stany ładowania (skeleton) i puste stany. Konfigurowalny dla różnych typów danych (budżety, transakcje).
*   **`Modal.vue`:** Podstawowy komponent modalny opakowujący `Shadcn Dialog`, zapewniający spójny wygląd i zachowanie (np. zarządzanie focusem).
*   **`BudgetForm.vue`, `TransactionForm.vue`, `CategoryForm.vue`:** Komponenty formularzy z logiką walidacji (zintegrowane z `vee-validate`/`Zod`) dla poszczególnych encji. Wykorzystywane wewnątrz modali.
*   **`StatsCard.vue`:** Komponent do wyświetlania pojedynczej metryki statystycznej.
*   **`LimitProgressBar.vue`:** Opakowanie na `Shadcn Progress` z logiką zmiany wyglądu w zależności od procentu wykorzystania limitu (>80%).
*   **`CategorySpendingChart.vue`:** Opakowanie na wybraną bibliotekę wykresów (np. Chart.js) do wyświetlania wykresu kołowego wydatków.
*   **`ConfirmDeleteDialog.vue`:** Reużywalny modal potwierdzenia usunięcia, konfigurowalny dla różnych zasobów (z opcjonalnym wyborem polityki dla kategorii).
