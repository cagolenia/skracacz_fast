PRD: System Skracania Linków (Micro-URL)
Wersja: 1.0
Status: Draft
Właściciel Projektu: Backend Developer
1. Cel projektu
Stworzenie wydajnego, skalowalnego systemu do skracania długich adresów URL, który dostarcza szczegółowych informacji analitycznych o ruchu, zachowując przy tym minimalne opóźnienia przy przekierowaniach.
2. Grupy użytkowników
Użytkownik anonimowy: Może zostać przekierowany po kliknięciu w krótki link.

Użytkownik zarejestrowany: Może tworzyć, usuwać i edytować własne linki oraz przeglądać statystyki.

Administrator: Może zarządzać wszystkimi linkami i monitorować obciążenie systemu.

3. Wymagania funkcjonalne (User Stories)
3.1 Zarządzanie linkami (Link Management)
Tworzenie: Użytkownik przesyła długi URL i otrzymuje unikalny, krótki token (np. bit.ly/3xYz1).
Własne aliasy: Możliwość zdefiniowania własnej końcówki linku (np. bit.ly/moje-portfolio).
Wygasanie: Możliwość ustawienia daty ważności linku, po której przestanie on działać.
CRUD: Użytkownik może przeglądać listę swoich linków i usuwać te nieaktywne.

3.2 Przekierowania (Redirection)
Wydajność: Przekierowanie (HTTP 301/302) musi odbywać się w czasie poniżej 50ms.
Obsługa błędów: Jeśli link nie istnieje lub wygasł, system wyświetla dedykowaną stronę 404.

3.3 Analityka (Analytics)
Zliczanie kliknięć: Każde użycie linku musi zostać odnotowane.
Metadane: System zbiera informacje o:
Kraju pochodzenia (na podstawie IP).
Typie urządzenia (Mobile/Desktop).
Refererze (skąd użytkownik przyszedł).

Pulpit nawigacyjny: Wykresy liczby kliknięć w czasie dla każdego linku.
4. Wymagania niefunkcjonalne
Skalowalność: System musi obsługiwać do 1000 przekierowań na sekundę (RPS).
Dostępność: 99.9% czasu działania (High Availability).
Bezpieczeństwo:
Zabezpieczenie przed brute-force (zgadywaniem tokenów).
Walidacja adresów URL (ochrona przed złośliwym oprogramowaniem).
Interfejs: API zgodne ze standardem RESTful, udokumentowane w Swaggerze.

5. Architektura wysokopoziomowa (Zgodna z ADR) Mikroserwisy
Service A (Zarządzanie): FastAPI + PostgreSQL.
Service B (Przekierowania): FastAPI + Redis.
Service C (Analityka): FastAPI + ClickHouse lub PostgreSQL (zoptymalizowany pod zapis).
Komunikacja: RabbitMQ do asynchronicznego przesyłania zdarzeń o kliknięciach.

6. Kryteria sukcesu
Średni czas odpowiedzi serwisu przekierowań < 30ms.
Poprawne przetworzenie 100% zdarzeń analitycznych przez kolejkę.

7.Struktura folderów projektu
skracacz_fast/
├── services/
│   ├── link_management/        # Serwis CRUD (Zarządzanie linkami)
│   │   ├── src/
│   │   │   ├── api/            # Endpointy FastAPI
│   │   │   ├── core/           # Konfiguracja, ustawienia (pydantic-settings)
│   │   │   ├── models/         # Modele bazy danych (SQLAlchemy/SQLModel)
│   │   │   ├── schemas/        # Schematy Pydantic (Request/Response)
│   │   │   ├── services/       # Logika biznesowa
│   │   │   └── main.py         # Punkt wejścia aplikacji
│   │   ├── tests/              # Testy jednostkowe i integracyjne
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── redirection/            # Serwis szybkich przekierowań
│   │   ├── src/
│   │   │   ├── cache/          # Logika obsługi Redisa
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── analytics/              # Serwis statystyk
│       ├── src/
│       │   ├── worker.py       # Konsument kolejki (np. Celery/RabbitMQ)
│       │   └── main.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── common/                     # Wspólne biblioteki (opcjonalnie)
│   └── shared_schemas/         # Wspólne modele danych między serwisami
│
├── docker-compose.yml          # Orkiestracja wszystkich usług
├── .env                        # Globalne zmienne środowiskowe
└── .gitignore

