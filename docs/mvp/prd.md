# Dokument wymagań produktu (PRD) - Budget Buddy

## 1. Przegląd produktu
Budget Buddy to aplikacja webowa wspierająca użytkowników w zarządzaniu finansami osobistymi. Jej głównym celem jest umożliwienie monitorowania wydatków, przypisywania transakcji do kategorii, generowania rekomendacji budżetowych oraz dostarczanie statystyk wspierających kontrolę nad budżetem. Aplikacja jest skierowana do osób, które chcą świadomie zarządzać swoimi finansami i osiągać cele oszczędnościowe.

## 2. Problem użytkownika
Użytkownicy często mają trudności z efektywnym zarządzaniem swoimi finansami, co prowadzi do:
- Nieprzewidzianych przekroczeń budżetu.
- Braku świadomości struktury wydatków.
- Trudności w osiąganiu celów finansowych, takich jak oszczędzanie określonej kwoty w miesiącu.

Budget Buddy rozwiązuje te problemy poprzez:
- Monitorowanie wydatków w ramach określonego budżetu miesięcznego.
- Przypisywanie transakcji do kategorii w celu lepszego wglądu w strukturę wydatków.
- Generowanie prostych rekomendacji budżetowych wspieranych przez generatywne AI.
- Dostarczanie statystyk takich jak dzienny limit wydatków oraz średnia/mediana wydatków w poszczególnych kategoriach.

## 3. Wymagania funkcjonalne
### MVP
1. **Dodawanie budżetu miesięcznego**:
   - Użytkownik definiuje całkowity budżet na dany miesiąc.
   - Dodając budżet, użytkownik musi zdefiniować przynajmniej jedną kategorię wydatków oraz cel finansowy (np. oszczędzenie określonej kwoty).
2. **Przypisywanie kategorii do budżetu**:
   - Możliwość tworzenia kategorii wydatków (np. jedzenie, transport) i przypisywania limitów do każdej z nich.
3. **Dodawanie transakcji**:
   - Formularz z następującymi polami:
     - Kwota.
     - Kategoria (wybór z listy zdefiniowanych kategorii).
     - Data transakcji (komponent kalendarza z walidacją daty).
     - Opcjonalny opis.
   - Walidacja daty na froncie i backendzie; obsługa błędów HTTP Bad Request.
4. **Rekomendacje budżetowe**:
   - Proste rekomendacje generowane przez AI na podstawie bieżącego budżetu i celów finansowych użytkownika.
   - Logowanie czasu wygenerowania rekomendacji oraz obsługa błędów.
5. **Statystyki**:
   - Obliczanie salda wydatków.
   - Wyliczanie średniej i mediany wydatków dla poszczególnych kategorii.
   - Wyświetlanie dziennej kwoty, którą użytkownik może wykorzystać, aby nie przekroczyć limitu.
6. **Podstawowy interfejs użytkownika**:
   - Formularze do dodawania budżetu, kategorii i transakcji.
   - Widok bieżącego stanu budżetu (wydane/pozostałe środki).
   - Wyświetlanie rekomendacji oraz statystyk w formie tekstowej i graficznej.
7. **Autentykacja użytkownika**:
   - Logowanie za pomocą emaila i hasła przy użyciu JWT tokenów.
8. **Lista transakcji**:
   - Użytkownik może zobaczyć listę wszystkich transakcji dodanych do budżetu wraz z opcjami edycji/usunięcia każdej z nich.
9. **Edycja/usuwanie transakcji**:
   - Użytkownik może edytować istniejące transakcje za pomocą formularza lub usuwać je z listy.

## 4. Granice produktu
### Zakres MVP
- Obsługa jednej waluty (domyślnie PLN).
- Brak analizy danych historycznych i zaawansowanej analityki finansowej.
- Brak integracji z bankami oraz automatycznego pobierania danych o transakcjach.
- Brak zaawansowanych wizualizacji danych (interaktywne wykresy, dashboardy).
- Brak personalizacji rekomendacji na podstawie preferencji użytkownika.

## 5. Historyjki użytkowników
### US-001: Logowanie użytkownika
**Opis**: Jako użytkownik chcę się zalogować do aplikacji za pomocą emaila i hasła, aby uzyskać dostęp do mojego konta.  
**Kryteria akceptacji**:  
- Użytkownik może zalogować się za pomocą poprawnych danych uwierzytelniających (email, hasło).  
- W przypadku błędnych danych wyświetlana jest odpowiednia notyfikacja.  
- Token JWT jest generowany po pomyślnym zalogowaniu.

### US-002: Tworzenie budżetu miesięcznego
**Opis**: Jako użytkownik chcę utworzyć nowy budżet miesięczny, aby móc monitorować moje wydatki i realizować cele finansowe.  
**Kryteria akceptacji**:  
- Użytkownik może określić całkowity budżet na dany miesiąc.  
- Użytkownik musi dodać przynajmniej jedną kategorię wydatków wraz z limitem dla każdej z nich.  
- Użytkownik musi określić cel finansowy związany z budżetem (np. oszczędzenie określonej kwoty).

### US-003: Dodawanie transakcji
**Opis**: Jako użytkownik chcę dodać nową transakcję, aby śledzić moje wydatki w ramach ustalonego budżetu.  
**Kryteria akceptacji**:  
- Użytkownik może dodać transakcję z poprawnymi polami (kwota, kategoria, data).  
- Data musi mieścić się w zakresie bieżącego miesiąca; walidacja na froncie i backendzie.  
- Widok budżetu synchronizuje się natychmiast po dodaniu transakcji.

### US-004: Generowanie rekomendacji budżetowych
**Opis**: Jako użytkownik chcę otrzymać rekomendacje dotyczące mojego budżetu, aby lepiej zarządzać moimi finansami.  
**Kryteria akceptacji**:  
- Rekomendacje są generowane na podstawie bieżących danych i celów finansowych użytkownika.  
- W przypadku błędu wyświetlana jest odpowiednia notyfikacja.

### US-005: Wyświetlanie statystyk
**Opis**: Jako użytkownik chcę zobaczyć statystyki dotyczące moich wydatków, aby lepiej kontrolować mój budżet.  
**Kryteria akceptacji**:  
- Statystyki obejmują dzienny limit wydatków oraz średnią/medianę dla poszczególnych kategorii.  
- Wyświetlana jest dzienna kwota, którą użytkownik może wykorzystać, aby nie przekroczyć salda.  
- Saldo ujemne oraz informacja "przekroczono" są wyróżniane kolorem czerwonym.

### US-006: Edycja transakcji
**Opis**: Jako użytkownik chcę móc edytować istniejącą transakcję, aby poprawić błędy lub zmienić jej szczegóły.  
**Kryteria akceptacji**:  
- Użytkownik może przejść do listy transakcji z widoku budżetu.  
- Obok każdej transakcji na liście znajduje się opcja "Edytuj".  
- Kliknięcie "Edytuj" otwiera formularz dodawania transakcji z wypełnionymi polami odpowiadającymi wybranej transakcji.  
- Formularz działa zgodnie z zasadami tworzenia nowej transakcji (walidacja danych, synchronizacja widoku po zapisaniu zmian).  

### US-007: Usuwanie transakcji
**Opis**: Jako użytkownik chcę móc usunąć istniejącą transakcję, aby usunąć błędnie dodane dane.  
**Kryteria akceptacji**:  
- Obok każdej transakcji na liście znajduje się opcja "Usuń".  
- Kliknięcie "Usuń" usuwa wybraną transakcję po potwierdzeniu przez użytkownika (np. modalem).  

### US-008: Wyświetlanie szczegółów transakcji
**Opis**: Jako użytkownik chcę móc zobaczyć szczegóły wybranej transakcji w trybie tylko do odczytu, aby przejrzeć jej pełne dane.  
**Kryteria akceptacji**:  
- Kliknięcie na element listy otwiera modal ze szczegółami wybranej transakcji w trybie tylko do odczytu (bez możliwości edycji).  

## 6. Metryki sukcesu
1. 90% użytkowników tworzy miesięczny budżet wraz z kategoriami oraz dodaje wydatki na bieżąco.
2. 70% użytkowników korzysta z funkcji generowania rekomendacji za pomocą AI.
3. Synchronizacja widoku po dodaniu/edycji/usunięciu transakcji odbywa się płynnie i bez zauważalnych opóźnień.
