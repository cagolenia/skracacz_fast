Utwórz plik .env dla zmiennych środowiskowych (bazy danych, klucze).
Zainstaluj Docker i Docker Compose na komputerze.
Utwórz plik docker-compose.yml w głównym folderze.
Zdefiniuj w Docker Compose usługę PostgreSQL (dla metadanych).
Zdefiniuj w Docker Compose usługę Redis (jako cache i broker).
⚙️ Faza 2: Pierwszy mikroserwis – Link Management (Kroki 11-20)
Wejdź do services/link_management i stwórz requirements.txt.
Dodaj fastapi, uvicorn, sqlalchemy, pydantic.
Stwórz Dockerfile dla tego serwisu.
Skonfiguruj Pydantic Settings do odczytu zmiennych z .env.
Stwórz plik database.py (inicjalizacja SQLAlchemy Engine).
Zdefiniuj model bazy danych Link (id, long_url, short_code, created_at).
Stwórz skrypt do automatycznej kreacji tabel w bazie.
Napisz pierwszy endpoint POST /links (przyjmujący długi URL).
Napisz funkcję generującą unikalny short_code (np. przy użyciu nanoid lub uuid).
Przetestuj zapisywanie linków do bazy przez Swagger UI (/docs).
🚄 Faza 3: Drugi mikroserwis – Redirection (Kroki 21-30)
Stwórz requirements.txt w services/redirection (dodaj redis).
Skonfiguruj połączenie z Redis w tym serwisie.
Napisz endpoint GET /{short_code}.
Zaimplementuj logikę: najpierw sprawdź kod w Redis.
Zaimplementuj "fallback": jeśli brak w Redis, zapytaj Link Management przez HTTP.
Napisz logikę zapisu brakującego klucza do Redis (caching).
Zwróć nagłówek HTTP 301 Moved Permanently.
Dodaj obsługę błędu 404, jeśli kod nie istnieje w żadnym źródle.
Stwórz Dockerfile dla serwisu przekierowań.
Dodaj oba serwisy do głównego docker-compose.yml.
📩 Faza 4: Komunikacja i Kolejki (Kroki 31-40)
Dodaj RabbitMQ (lub Redis Streams) do docker-compose.yml.
W serwisie redirection zainstaluj bibliotekę do obsługi kolejki (np. pika lub taskiq).
Napisz funkcję "emitującą" zdarzenie LinkVisited po każdym przekierowaniu.
Stwórz trzeci serwis: analytics.
W analytics zdefiniuj model bazy dla statystyk (link_id, timestamp, ip, user_agent).
Napisz "workera", który nasłuchuje na kolejce RabbitMQ.
Zaimplementuj funkcję zapisu danych z kolejki do bazy analitycznej.
Stwórz endpoint GET /stats/{short_code} w serwisie analitycznym.
Skonfiguruj CORS w FastAPI, aby serwisy mogły ze sobą rozmawiać.
Uruchom cały stos komendą docker-compose up --build.
🛡️ Faza 5: Szlifowanie i Produkcja (Kroki 41-50)
Dodaj walidację adresów URL (czy na pewno są poprawne).
Zaimplementuj sprawdzanie duplikatów (ten sam URL = ten sam kod).
Dodaj middleware do logowania zapytań w każdym serwisie.
Stwórz folder tests/ i napisz pierwszy test jednostkowy w Pytest.
Napisz test integracyjny: czy kliknięcie w link faktycznie generuje wpis w analityce.
Dodaj Healthchecks w Dockerze dla każdej usługi.
Zoptymalizuj obrazy Dockerowe (użyj python:3.11-alpine lub slim).
Stwórz plik README.md z instrukcją instalacji.
Skonfiguruj prosty skrypt do ładowania danych testowych.
