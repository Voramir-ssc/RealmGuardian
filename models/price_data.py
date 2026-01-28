from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)  # Blizzard Item ID
    name = Column(String, nullable=False)
    expansion = Column(String)
    min_price_threshold = Column(Float, default=0.0) # Alert if price drops below this

    prices = relationship("Price", back_populates="item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}')>"

class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    price = Column(Float, nullable=False)  # Average Buyout in Gold (or Copper)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    item = relationship("Item", back_populates="prices")

    def __repr__(self):
        return f"<Price(item_id={self.item_id}, price={self.price}, time='{self.timestamp}')>"
