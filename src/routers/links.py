from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi.responses import RedirectResponse
from src.database.db import SessionLocal
from src.database.models import Link
from src.services.link import generate_short_code
from src.cache.redis import r
from src.routers.users import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/shorten")
def create_short_link(
    original_url: str,
    custom_alias: str = None,
    expires_at: datetime = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if custom_alias:
        existing = db.query(Link).filter(Link.short_code == custom_alias).first()
        if existing:
            raise HTTPException(status_code=400, detail="Custom alias уже используется")
        short_code = custom_alias
    else:
        short_code = generate_short_code()

    new_link = Link(
        original_url=original_url,
        short_code=short_code,
        user_id=current_user.id,
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at,
        click_count=0
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    r.set(short_code, original_url)

    return {"short_code": new_link.short_code, "original_url": new_link.original_url}

@router.get("/{short_code}")
def redirect_link(short_code: str, db: Session = Depends(get_db)):
    cached_url = r.get(short_code)
    if cached_url:
        return RedirectResponse(url=cached_url)
    
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    
    if link.expires_at and datetime.now(timezone.utc) > link.expires_at:
        raise HTTPException(status_code=410, detail="Ссылка истекла")
    
    link.click_count += 1
    link.last_accessed = datetime.now(timezone.utc)
    db.commit()

    r.set(short_code, link.original_url)
    return RedirectResponse(url=link.original_url)

@router.put("/{short_code}")
def update_link(
    short_code: str,
    original_url: str,
    expires_at: datetime = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    if link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к изменению этой ссылки")
    
    link.original_url = original_url
    link.expires_at = expires_at
    db.commit()
    r.set(short_code, original_url)
    return {"message": "Ссылка обновлена", "short_code": short_code, "original_url": original_url}

@router.delete("/{short_code}")
def delete_link(short_code: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    if link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к удалению этой ссылки")
    
    db.delete(link)
    db.commit()
    r.delete(short_code)
    return {"message": "Ссылка удалена"}

@router.get("/{short_code}/stats")
def get_link_stats(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    
    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "expires_at": link.expires_at,
        "click_count": link.click_count,
        "last_accessed": link.last_accessed
    }

@router.get("/search")
def search_link(original_url: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.original_url == original_url).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    return link
