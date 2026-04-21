import string
import secrets
from nanoid import generate


def generate_short_code(length: int = 7, use_nanoid: bool = True) -> str:
    """
    Generuje unikalny krótki kod dla URL.
    
    Args:
        length: Długość generowanego kodu (domyślnie 7)
        use_nanoid: Czy użyć nanoid (bardziej URL-friendly) czy secrets
    
    Returns:
        Unikalny krótki kod
    
    Examples:
        >>> code = generate_short_code()
        >>> len(code)
        7
        >>> code = generate_short_code(length=10, use_nanoid=False)
        >>> len(code)
        10
    """
    if use_nanoid:
        # Nanoid generuje URL-safe stringi
        # Używamy tylko liter i cyfr (bez znaków specjalnych)
        alphabet = string.ascii_letters + string.digits
        return generate(alphabet, length)
    else:
        # Alternatywnie używamy secrets (bardziej bezpieczne, ale mniej czytelne)
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_unique_code(existing_codes: set, length: int = 7, max_attempts: int = 10) -> str:
    """
    Generuje unikalny kod, który nie istnieje w podanym zbiorze.
    
    Args:
        existing_codes: Zbiór już istniejących kodów
        length: Długość kodu
        max_attempts: Maksymalna liczba prób generacji
    
    Returns:
        Unikalny kod
    
    Raises:
        ValueError: Jeśli nie udało się wygenerować unikalnego kodu
    """
    for _ in range(max_attempts):
        code = generate_short_code(length)
        if code not in existing_codes:
            return code
    
    raise ValueError(f"Nie udało się wygenerować unikalnego kodu po {max_attempts} próbach")
