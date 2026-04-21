import validators
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class URLValidator:
    """Walidator URL z dodatkowymi sprawdzeniami bezpieczeństwa"""
    
    # Lista zabronicznych domen (malware, phishing, etc.)
    BLACKLISTED_DOMAINS = [
        'malware.com',
        'phishing.test',
        # Dodaj więcej w produkcji lub użyj zewnętrznego API
    ]
    
    # Lista zabronionych schematów
    ALLOWED_SCHEMES = ['http', 'https']
    
    @staticmethod
    def validate_url(url: str) -> tuple[bool, str]:
        """
        Waliduje URL pod kątem poprawności i bezpieczeństwa.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Podstawowa walidacja
        if not url or not isinstance(url, str):
            return False, "URL nie może być pusty"
        
        # Sprawdź długość
        if len(url) < 10:
            return False, "URL jest za krótki (minimum 10 znaków)"
        
        if len(url) > 2048:
            return False, "URL jest za długi (maksimum 2048 znaków)"
        
        # Walidacja za pomocą biblioteki validators
        if not validators.url(url):
            return False, "URL jest niepoprawny"
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, f"Błąd parsowania URL: {str(e)}"
        
        # Sprawdź schemat
        if parsed.scheme not in URLValidator.ALLOWED_SCHEMES:
            return False, f"Niedozwolony schemat. Dozwolone: {', '.join(URLValidator.ALLOWED_SCHEMES)}"
        
        # Sprawdź domenę
        if not parsed.netloc:
            return False, "URL musi zawierać domenę"
        
        # Sprawdź czarną listę domen
        domain = parsed.netloc.lower()
        for blocked in URLValidator.BLACKLISTED_DOMAINS:
            if blocked in domain:
                return False, f"Domena {domain} jest zablokowana"
        
        # Sprawdź IP lokalne (opcjonalnie)
        if any(x in domain for x in ['localhost', '127.0.0.1', '0.0.0.0']):
            logger.warning(f"Próba utworzenia linku do localhost: {url}")
            # W produkcji możesz to zablokować
            # return False, "Nie można skracać linków do localhost"
        
        return True, ""
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalizuje URL (usuwa nadmiarowe spacje, dodaje schemat jeśli brak).
        """
        url = url.strip()
        
        # Dodaj https:// jeśli brak schematu
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
