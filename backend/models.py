"""
models.py
Defines the SQLAlchemy ORM models representing the database schema.
Includes models for WoW Tokens, Characters, Tracked Items, and Price History.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class WowTokenHistory(Base):
    __tablename__ = "wow_token_history"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Integer, nullable=False)  # Stored in copper/raw value
    last_updated_timestamp = Column(Integer, nullable=False) # Blizzard timestamp
    region = Column(String, default="eu")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TrackedItem(Base):
    __tablename__ = "tracked_items"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    icon_url = Column(String, nullable=True)
    quality = Column(String, nullable=True) # e.g. "EPIC", "RARE"

    price_history = relationship("ItemPriceHistory", back_populates="item")

class ItemPriceHistory(Base):
    __tablename__ = "item_price_history"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("tracked_items.id"))
    buyout = Column(Integer, nullable=False) # Gold value or copper? Usually copper in API
    quantity = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    item = relationship("TrackedItem", back_populates="price_history")

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    blizzard_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    realm = Column(String, nullable=False)
    class_name = Column(String, nullable=True)
    level = Column(Integer, nullable=True)
    item_level = Column(Integer, default=0)
    equipment = Column(String, nullable=True) # Will store compressed JSON
    gold = Column(Integer, default=0) # Stored in copper
    played_time = Column(Integer, default=0) # Seconds
    icon_url = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class AccountGoldHistory(Base):
    __tablename__ = "account_gold_history"

    id = Column(Integer, primary_key=True, index=True)
    total_gold = Column(Integer, nullable=False) # Stored in copper
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
