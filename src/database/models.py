from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    links = relationship("Link", back_populates="owner")

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_url = Column(String)
    short_code = Column(String, unique=True, index=True)
    custom_alias = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    click_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="links")
    preview = relationship("LinkPreview", back_populates="link", uselist=False)

class LinkPreview(Base):
    __tablename__ = "link_previews"
    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("links.id"))
    title = Column(String)
    description = Column(Text)
    image_url = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    link = relationship("Link", back_populates="preview")
