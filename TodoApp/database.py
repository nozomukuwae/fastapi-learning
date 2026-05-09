import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:' + DATABASE_PASSWORD + '@localhost/TodoApplicationDatabase'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
