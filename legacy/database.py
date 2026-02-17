from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# Import models to register them with metadata
# Note: This export is needed even if not used directly here


def init_db(db_name='realm_guardian.db'):
    import sys
    import os
    from models.character import Character
    from models.price_data import Item, Price, TokenPrice

    # Determine application root
    if getattr(sys, 'frozen', False):
        # If running as compiled exe, use the directory of the executable
        application_path = os.path.dirname(sys.executable)
    else:
        # If running as script, use the directory of this file
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    db_path = os.path.join(application_path, db_name)
    
    # SQLite URL requires 3 slashes for relative, 4 for absolute (on *nix), but on Windows absolute paths work with 3 slashes if drive letter is present
    # Usually 'sqlite:///C:\\path\\to\\db' works.
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
