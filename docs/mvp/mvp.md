## **Główny problem**

Aplikacja "Budget Buddy" pomaga użytkownikom w zarządzaniu finansami osobistymi poprzez:

- Monitorowanie wydatków w ramach określonego budżetu miesięcznego.
- Przypisywanie transakcji do kategorii, co pozwala na lepszy wgląd w strukturę wydatków.
- Generowanie prostych rekomendacji budżetowych, które
pomagają użytkownikowi osiągnąć jego cele finansowe (np. oszczędzanie
określonej kwoty w miesiącu).
- Dostarczanie statystyk, takich jak dzienny limit
wydatków oraz średnia/mediana wydatków w poszczególnych kategoriach, co
wspiera kontrolę nad budżetem.

## **Najmniejszy zestaw funkcjonalności**

## Co wchodzi w skład MVP?

1. **Dodawanie budżetu miesięcznego**:
    - Użytkownik może określić całkowity budżet, którym dysponuje w danym miesiącu.
2. **Przypisywanie kategorii do budżetu**:
    - Użytkownik może zdefiniować kategorie wydatków (np. jedzenie, transport, rozrywka) oraz przypisać do nich limity.
3. **Dodawanie transakcji**:
    - Użytkownik może ręcznie dodawać transakcje z następującymi polami:
        - Kwota.
        - Kategoria (wybór z listy zdefiniowanych kategorii).
        - Data transakcji.
        - Opcjonalny opis (np. "Kolacja w restauracji").
4. **Rekomendacje budżetowe**:
    - Proste rekomendacje generowane na podstawie bieżącego budżetu i celów finansowych użytkownika:
        - Informowanie o potencjalnych przekroczeniach limitów w kategoriach.
        - Sugestie dotyczące ograniczenia wydatków lub przesunięcia środków między kategoriami. Integracja z **GEN AI**
        
        
5. **Statystyki**:
    - Obliczanie pozostałej kwoty do wykorzystania na
    pozostałe dni miesiąca, aby nie przekroczyć budżetu (np. dzienny limit
    wydatków).
    - Wyliczanie średniej i mediany wydatków dla poszczególnych kategorii.
6. **Podstawowy interfejs użytkownika**:
    - Formularze do dodawania budżetu, kategorii i transakcji.
    - Sekcja prezentująca bieżący stan budżetu (np. ile zostało wydane, ile pozostało do wydania).
    - Wyświetlanie rekomendacji oraz statystyk w formie tekstowej i graficznej.
7. **Autentykacja i autoryzacja użytkownika**:
    - System logowania i rejestracji użytkowników, aby zapewnić prywatność danych.

## Co nie wchodzi w skład MVP?

1. **Dane historyczne**:
    - Analiza danych historycznych i generowanie zaawansowanych statystyk na ich podstawie (np. trendy wydatków z kilku miesięcy).
2. **Zaawansowana analityka finansowa**:
    - Prognozy wydatków na przyszłość.
    - Wykrywanie anomalii lub nietypowych wzorców wydatków.
3. **Integracje z bankami**:
    - Automatyczne pobieranie danych o transakcjach z kont bankowych.
4. **Zaawansowane wizualizacje danych**:
    - Interaktywne wykresy czy zaawansowane dashboardy analityczne.
5. **Personalizacja rekomendacji na podstawie preferencji użytkownika**:
    - W MVP rekomendacje będą generowane na podstawie prostych reguł biznesowych, bez uwzględniania indywidualnych preferencji.
6. **Obsługa wielu walut lub skomplikowanych scenariuszy finansowych**:
    - Aplikacja będzie działać tylko dla jednej waluty (domyślnie PLN).

## **Kryteria sukcesu:**

- 90% użytkowników ma utworzony budżet miesięczny wraz z kategoriami oraz dodaje na bieżąco wydatki
- 70% użytkowników generuje sugestie budżetu za pomocą AI