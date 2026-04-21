"""
Skrypt do uruchamiania Link Management Service
"""
import sys
from pathlib import Path

# Dodaj katalog główny do PYTHONPATH
service_dir = Path(__file__).parent
sys.path.insert(0, str(service_dir))

if __name__ == "__main__":
    import uvicorn
    from src.core.config import settings
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level="info"
    )
