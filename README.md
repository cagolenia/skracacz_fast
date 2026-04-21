# System Skracania Linków (Micro-URL)

Wydajny, skalowalny system do skracania długich adresów URL z zaawansowaną analityką ruchu.

## 🏗️ Architektura

Projekt składa się z trzech mikroserwisów:

1. **Link Management** (Port 8001) - Zarządzanie linkami (CRUD)
2. **Redirection** (Port 8002) - Szybkie przekierowania
3. **Analytics** (Port 8003) - Statystyki i analityka

## 🚀 Technologie

- **FastAPI** - Framework dla API
- **PostgreSQL** - Baza danych dla metadanych
- **Redis** - Cache dla przekierowań
- **RabbitMQ** - Kolejka komunikatów
- **Docker** - Konteneryzacja

## 📋 Wymagania

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3+

## 🛠️ Instalacja (Tryb lokalny z .venv)

### 1. Sklonuj repozytorium i przejdź do katalogu projektu

```bash
cd c:\Users\Cezary\Documents\My\skracacz_fast
```

### 2. Utwórz wirtualne środowisko Python

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Uruchom infrastrukturę (PostgreSQL, Redis, RabbitMQ)

```bash
docker-compose up -d postgres redis rabbitmq
```

### 4. Zainstaluj zależności dla każdego serwisu

```powershell
# Link Management
cd services\link_management
pip install -r requirements.txt
cd ..\..

# Redirection
cd services\redirection
pip install -r requirements.txt
cd ..\..

# Analytics
cd services\analytics
pip install -r requirements.txt
cd ..\..
```

### 5. Uruchom serwisy (w osobnych terminalach)

```powershell
# Terminal 1 - Link Management
cd services\link_management
uvicorn src.main:app --reload --port 8001

# Terminal 2 - Redirection
cd services\redirection
uvicorn src.main:app --reload --port 8002

# Terminal 3 - Analytics
cd services\analytics
uvicorn src.main:app --reload --port 8003
```

## 🐳 Instalacja (Tryb Docker)

```bash
docker-compose up --build
```

## 📊 Dostęp do usług

- **Link Management API**: http://localhost:8001/docs
- **Redirection Service**: http://localhost:8002/{short_code}
- **Analytics API**: http://localhost:8003/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## 🧪 Testowanie

```bash
pytest tests/
```

## 📝 Przykłady użycia

### Utworzenie krótkiego linku

```bash
curl -X POST "http://localhost:8001/links" \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.example.com/very/long/url"}'
```

### Przekierowanie

```bash
curl -L "http://localhost:8002/abc123"
```

### Statystyki

```bash
curl "http://localhost:8003/stats/abc123"
```

## 📂 Struktura projektu

```
skracacz_fast/
├── services/
│   ├── link_management/     # Serwis CRUD
│   ├── redirection/         # Serwis przekierowań
│   └── analytics/           # Serwis analityki
├── common/                  # Wspólne biblioteki
├── docker-compose.yml
├── .env
└── README.md
```

## 🔧 Konfiguracja

Edytuj plik `.env` aby dostosować konfigurację:

- Dane dostępowe do bazy danych
- Porty serwisów
- Klucze API
- Tryb debug

## 📈 Wydajność

- Przekierowania: < 30ms średni czas odpowiedzi
- Obsługa: 1000+ RPS
- Dostępność: 99.9%

## 📄 Licencja

MIT
