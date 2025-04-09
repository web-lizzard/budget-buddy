Frontend - Astro z React dla komponentów interaktywnych:
- Astro 5 pozwala na tworzenie szybkich, wydajnych stron i aplikacji z minimalną ilością JavaScript
- React 19 zapewni interaktywność tam, gdzie jest potrzebna
- TypeScript 5 dla statycznego typowania kodu i lepszego wsparcia IDE
- Tailwind 4 pozwala na wygodne stylowanie aplikacji
- Shadcn/ui zapewnia bibliotekę dostępnych komponentów React, na których oprzemy UI

Backend - Python 3.13, uv FastAPI, DependencyInjector, Postgresql, alembic:
- uv jako bardzo szybki menadzer zalezności projektu
- fastapi zapewnia bardzo stabilne api, wspiera asynchronicznosc i podstawowe wstrzykiwanie zalezności
- dependency injector ułatwi zarządzanie zaleznosciami i zapewni odwrócenie sterowania
- stabilna baza danych sql, wiele dodatkowych opcji
- zarządzanie migracjami z alembic

AI - Komunikacja z modelami przez usługę Openrouter.ai:
- Dostęp do szerokiej gamy modeli (OpenAI, Anthropic, Google i wiele innych), które pozwolą nam znaleźć rozwiązanie zapewniające wysoką efektywność i niskie koszta
- Pozwala na ustawianie limitów finansowych na klucze API

CI/CD i Hosting:
- Github Actions do tworzenia pipeline’ów CI/CD
- DigitalOcean do hostowania aplikacji za pośrednictwem obrazu docker