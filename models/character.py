from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    realm = Column(String, nullable=False)
    race = Column(String)
    character_class = Column(String)  # 'class' is a reserved keyword
    profession_1 = Column(String)
    profession_2 = Column(String)
    status = Column(String, default="Active")

    def __repr__(self):
        return f"<Character(name='{self.name}', realm='{self.realm}', status='{self.status}')>"
