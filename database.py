from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

CONNECTION_URL = 'mysql+pymysql://wbuser:webuyuser@localhost/webuy'

# Connection to mysql server
# engine = create_engine(CONNECTION_URL, echo=True)
engine = create_engine(CONNECTION_URL)

# Creates session(connections)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class to extend in models
Base = declarative_base()

# Call this function to connect to database
def get_db():
    session=SessionLocal()
    try:
        yield session
    finally:
        session.close()