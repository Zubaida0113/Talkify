from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./talkify.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

#This code does 3 things:

#creates a connection to the SQLite database
#allows SQLite to work with FastAPI threads
#creates a session object you can use to query and modify data