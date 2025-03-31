from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from src.database.db import SessionLocal
from src.database.models import Link, LinkPreview
from src.routers.users import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{link_id}")
def create_link_preview(
    link_id: int,
    title: str,
    description: str,
    image_url: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    if link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к созданию предпросмотра для этой ссылки")
    
    preview = LinkPreview(
        link_id=link_id,
        title=title,
        description=description,
        image_url=image_url,
        created_at=datetime.now(timezone.utc)
    )
    db.add(preview)
    db.commit()
    db.refresh(preview)
    return preview

@router.get("/{link_id}")
def get_link_preview(link_id: int, db: Session = Depends(get_db)):
    preview = db.query(LinkPreview).filter(LinkPreview.link_id == link_id).first()
    if not preview:
        raise HTTPException(status_code=404, detail="Предпросмотр не найден")
    return preview
