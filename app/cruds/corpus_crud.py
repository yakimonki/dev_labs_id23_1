from sqlalchemy.orm import Session
from app.models.corpus import Corpus

def create_corpus(db: Session, corpus_name: str, text: str):
    corpus = Corpus(corpus_name=corpus_name, text=text)
    db.add(corpus)
    db.commit()
    db.refresh(corpus)
    return corpus

def get_all_corpuses(db: Session):
    return db.query(Corpus).all()

def get_corpus_by_id(db: Session, corpus_id: int):
    return db.query(Corpus).filter(Corpus.id == corpus_id).first()
