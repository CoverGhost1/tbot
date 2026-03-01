import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://...")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class UserLocation(Base):
    __tablename__ = "user_locations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    city_name = Column(String)  # Nama custom
    latitude = Column(Float)    # Koordinat
    longitude = Column(Float)   # Koordinat
    country = Column(String, default="Indonesia")
    created_at = Column(DateTime, default=datetime.now(pytz.UTC))
    updated_at = Column(DateTime, default=datetime.now(pytz.UTC), onupdate=datetime.now(pytz.UTC))

class RecipeHistory(Base):
    __tablename__ = "recipe_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, index=True)
    recipe_name = Column(String)
    searched_at = Column(DateTime, default=datetime.now(pytz.UTC))

# Buat tabel
Base.metadata.create_all(bind=engine)
