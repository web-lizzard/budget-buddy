## **Cel funkcjonalności**

Dostarczenie użytkownikowi natychmiastowych, 
praktycznych wskazówek dotyczących zarządzania budżetem, opartych 
wyłącznie na wprowadzonych przez niego danych, takich jak:

- Miesięczny budżet.
- Kategorie wydatków i ich limity.
- Cele finansowe (np. oszczędzanie określonej kwoty).

## **Dane wejściowe**

Użytkownik wprowadza dane ręcznie, co eliminuje potrzebę posiadania danych historycznych. Oto przykładowe dane wejściowe:

## 1. **Budżet miesięczny**

- Całkowita kwota dostępna do wydania w danym miesiącu (np. 5000 zł).

## 2. **Kategorie wydatków**

- Lista kategorii z przypisanymi limitami (np. jedzenie: 1500 zł, transport: 500 zł, rozrywka: 300 zł).
- Ewentualnie użytkownik może nie definiować limitów dla kategorii – aplikacja sama zaproponuje podział.

## 3. **Cel finansowy**

- Kwota, którą użytkownik chce zaoszczędzić w danym miesiącu (np. 1000 zł).

## 4. **Bieżące wydatki**

- Użytkownik ręcznie wprowadza swoje bieżące wydatki w poszczególnych kategoriach.

## **Logika działania**

Na podstawie tych danych aplikacja generuje proste 
rekomendacje dotyczące zarządzania budżetem i osiągania celów 
finansowych. Nie wymaga to skomplikowanego modelu AI – wystarczy 
zastosowanie reguł biznesowych oraz generatywnej AI do formułowania 
sugestii w bardziej "ludzkiej" formie.

## 1. **Podział budżetu**

- Jeśli użytkownik nie określił limitów dla kategorii,
aplikacja zaproponuje podział budżetu na podstawie ogólnych zasad
zarządzania finansami (np. reguła 50/30/20):
    - 50% na potrzeby (jedzenie, mieszkanie itp.).
    - 30% na przyjemności (rozrywka, hobby).
    - 20% na oszczędności.



## 2. **Generowanie rekomendacji**

Na podstawie prostych obliczeń aplikacja może sugerować:

- Ograniczenie wydatków w kategoriach, gdzie limity są bliskie przekroczenia.
- Przesunięcie środków między kategoriami.
- Propozycje zwiększenia oszczędności poprzez drobne zmiany w wydatkach.

## **Dane wyjściowe (dla użytkownika)**

Rekomendacje powinny być jasne i praktyczne, a ich forma może być bardziej "przyjazna" dzięki generatywnej AI. Oto przykłady:

## 1. **Ogólne wskazówki**

- "Twój miesięczny budżet wynosi 5000 zł. Aby osiągnąć cel oszczędnościowy (1000 zł), możesz przeznaczyć maksymalnie 4000 zł na
wydatki."
- "Zgodnie z regułą 50/30/20 sugerujemy następujący podział: potrzeby – 2500 zł, przyjemności – 1500 zł, oszczędności – 1000 zł."

## 2. **Rekomendacje dla poszczególnych kategorii**

- "Wydajesz już 80% swojego limitu na jedzenie (1200/1500 zł). Rozważ gotowanie w domu zamiast jedzenia poza domem."
- "Masz jeszcze 200 zł do wykorzystania w kategorii rozrywka – możesz pozwolić sobie na małą przyjemność!"

## 3. **Sugestie optymalizacji**

- "Jeśli ograniczysz wydatki na transport o 50 zł, będziesz bliżej osiągnięcia celu oszczędnościowego."
- "Rozważ ustalenie limitu na zakupy impulsowe – to pomoże Ci lepiej kontrolować budżet."

## **Przykład przepływu działania funkcji**

1. Użytkownik loguje się do aplikacji i przechodzi do sekcji "Stwórz budżet".
2. Wprowadza dane:
    - Budżet miesięczny: 5000 zł.
    - Kategorie i limity: jedzenie – 1500 zł, transport – 500 zł, rozrywka – brak limitu.
    - Cel oszczędnościowy: zaoszczędzić 1000 zł.
3. Aplikacja oblicza:
    - Dostępną kwotę do wydania: 4000 zł.
    - Proponowany podział budżetu: potrzeby – 2500 zł, przyjemności – 1500 zł.
4. Generatywna AI formułuje rekomendacje:
    - "Twój cel oszczędnościowy wynosi 1000 zł – aby go
    osiągnąć, staraj się nie przekraczać wydatków w kategoriach jedzenie i
    transport."
5. Wyniki są prezentowane użytkownikowi w formie tekstowej oraz graficznej (np. wykresy kołowe pokazujące podział budżetu).


## **Podsumowanie**
Funkcjonalność powinna być dostępna podczas tworzenia nowego budżetu oraz na życzenie klienta. 
W widoku "Aktywny budzet", jest mozliwość wygenerowania rekomendacji w takiej sytuacji system tworzy taką rekomendacje na podstawie danych dotyczących obecnego budżetu - nie bierze pod uwagę żadnych danych historycznych