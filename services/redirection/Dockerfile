FROM python:3.11-alpine

WORKDIR /app

# Instalacja zależności
RUN apk add --no-cache gcc musl-dev

# Kopiowanie requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu aplikacji
COPY . .

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Uruchomienie aplikacji
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
