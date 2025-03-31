from sqlalchemy import Column, Integer, String, Text
from app.db.session import Base

class Corpus(Base):
    __tablename__ = "corpuses"
    
    id = Column(Integer, primary_key=True, index=True)
    corpus_name = Column(String, unique=True, index=True)
    text = Column(Text)
