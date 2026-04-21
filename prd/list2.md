Faza 6: Zaawansowane Bezpieczeństwo (Kroki 51-58)
Rate Limiting: Dodaj limitowanie zapytań (np. 10 linków na minutę dla IP), aby uniknąć spamu.
API Key Authentication: Wprowadź klucze API dla serwisu zarządzania linkami.
Security Headers: Dodaj middleware w FastAPI (np. TrustedHostMiddleware, CORSMiddleware).
Data Sanitization: Wprowadź rygorystyczne oczyszczanie wejściowych URLi przed zapisem.
Encryption at Rest: Skonfiguruj szyfrowanie wrażliwych danych w bazie danych.
Secrets Management: Przenieś hasła z .env do bezpiecznego magazynu (np. HashiCorp Vault lub AWS Secrets Manager).
SQL Injection Protection: Upewnij się, że wszystkie zapytania korzystają z ORM lub parametrów bindowanych.
Dependency Scanning: Skonfiguruj safety lub snyk do skanowania bibliotek pod kątem podatności.
📊 Faza 7: Monitoring i Obserwowalność (Kroki 59-66)
Centralized Logging: Skonfiguruj wysyłanie logów z kontenerów do ELK Stack (Elasticsearch, Logstash, Kibana).
Prometheus Metrics: Dodaj endpoint /metrics w każdym serwisie (użyj prometheus_fastapi_instrumentator).
Grafana Dashboard: Stwórz wizualizację liczby przekierowań i błędów 404 w czasie rzeczywistym.
Tracing: Zaimplementuj OpenTelemetry (Jaeger), aby śledzić ścieżkę zapytania przez wszystkie serwisy.
Alerting: Ustaw powiadomienia (Slack/Email), gdy Redirect Service przestanie odpowiadać.
Sentry Integration: Dodaj raportowanie błędów w kodzie (Tracebacków) bezpośrednio do Sentry.
Database Profiling: Sprawdź najwolniejsze zapytania SQL i dodaj brakujące indeksy.
Healthcheck UI: Skonfiguruj prosty dashboard monitorujący status "Health" wszystkich mikrousług.
🚀 Faza 8: Optymalizacja i Infrastruktura (Kroki 67-75)
Horizontal Pod Autoscaling: Przygotuj manifesty Kubernetes (K8s) dla skalowania serwisu przekierowań.
Load Balancing: Skonfiguruj Nginx lub Traefik jako Reverse Proxy i Load Balancer.
CI/CD Pipeline: Stwórz automatyzację w GitHub Actions (testy -> budowa obrazu -> push do rejestru).
Blue-Green Deployment: Przygotuj strategię wdrażania nowych wersji bez przestojów.
Database Migrations: Wprowadź narzędzie Alembic do zarządzania zmianami w schemacie bazy.
Cache Warming: Napisz skrypt, który po restarcie ładuje najpopularniejsze linki z DB do Redisa.
CDN Integration: Rozważ użycie CDN dla statycznych elementów (jeśli system ma UI).
Documentation Versioning: Wprowadź wersjonowanie API (np. /v1/links, /v2/links).
Performance Testing: Przeprowadź testy obciążeniowe przy użyciu Locust, aby znaleźć "wąskie gardło".
