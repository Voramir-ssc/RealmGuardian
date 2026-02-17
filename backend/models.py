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
