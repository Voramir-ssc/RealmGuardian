from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# Import models to register them with metadata
# Note: This export is needed even if not used directly here


def init_db(db_name='realm_guardian.db'):
    from models.character import Character
    from models.price_data import Item, Price, TokenPrice
    engine = create_engine(f'sqlite:///{db_name}')
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
