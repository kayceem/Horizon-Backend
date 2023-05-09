from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

CONNECTION_URI = 'mysql+pymysql://wbuser:webuyuser@localhost/webuy'

# Connection to mysql server
# engine = create_engine(CONNECTION_URL, echo=True)
engine = create_engine(CONNECTION_URI, connect_args={"init_command": "SET time_zone='+00:00';"})

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