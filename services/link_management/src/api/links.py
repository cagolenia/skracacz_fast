from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.schemas.link import (
    LinkCreate,
    LinkResponse,
    LinkUpdate,
    LinkListResponse
)
from src.services.link_service import LinkService
from src.core.config import settings

router = APIRouter(tags=["links"])


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def create_link(link_data: LinkCreate, db: Session = Depends(get_db)):
    """
    Tworzy nowy skrócony link.
    
    - **long_url**: Długi URL do skrócenia
    - **custom_alias**: Opcjonalny własny alias (zamiast losowego kodu)
    - **expires_at**: Opcjonalna data wygaśnięcia linku
    """
    try:
        link = LinkService.create_link(db, link_data)
        
        # Dodaj pełny URL do odpowiedzi
        response = LinkResponse.model_validate(link)
        response.short_url = f"http://localhost:8002/{link.short_code}"
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{short_code}", response_model=LinkResponse)
def get_link(short_code: str, db: Session = Depends(get_db)):
    """
    Pobiera informacje o linku po jego krótkim kodzie.
    """
    link = LinkService.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link nie został znaleziony")
    
    response = LinkResponse.model_validate(link)
    response.short_url = f"http://localhost:8002/{link.short_code}"
    
    return response


@router.get("/", response_model=LinkListResponse)
def list_links(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Pobiera listę wszystkich linków z paginacją.
    
    - **skip**: Liczba rekordów do pominięcia
    - **limit**: Maksymalna liczba zwracanych rekordów
    - **active_only**: Czy zwracać tylko aktywne linki
    """
    links = LinkService.get_links(db, skip=skip, limit=limit, active_only=active_only)
    
    from src.models.link import Link
    if active_only:
        total = db.query(Link).filter(Link.is_active == True).count()
    else:
        total = db.query(Link).count()
    
    # Dodaj short_url do każdego linku
    items = []
    for link in links:
        response = LinkResponse.model_validate(link)
        response.short_url = f"http://localhost:8002/{link.short_code}"
        items.append(response)
    
    return LinkListResponse(
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        items=items
    )


@router.put("/{link_id}", response_model=LinkResponse)
def update_link(link_id: int, link_update: LinkUpdate, db: Session = Depends(get_db)):
    """
    Aktualizuje istniejący link.
    """
    link = LinkService.update_link(db, link_id, link_update)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link nie został znaleziony")
    
    response = LinkResponse.model_validate(link)
    response.short_url = f"http://localhost:8002/{link.short_code}"
    
    return response


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(link_id: int, db: Session = Depends(get_db)):
    """
    Usuwa link (soft delete - dezaktywuje).
    """
    success = LinkService.delete_link(db, link_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link nie został znaleziony")
    
    return None


@router.post("/{short_code}/click", status_code=status.HTTP_200_OK)
def increment_click(short_code: str, db: Session = Depends(get_db)):
    """
    Inkrementuje licznik kliknięć dla danego linku.
    Ten endpoint jest używany wewnętrznie przez serwis Redirection.
    """
    success = LinkService.increment_clicks(db, short_code)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link nie został znaleziony")
    
    return {"message": "Licznik kliknięć zaktualizowany"}
