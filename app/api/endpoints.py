from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import corpus_schema, search_schema
from app.cruds import corpus_crud
from app.db.session import get_db
from app.services import fuzzy_search
import time

router = APIRouter()

@router.post("/upload_corpus", response_model=corpus_schema.UploadCorpusResponse)
def upload_corpus(payload: corpus_schema.UploadCorpusRequest, db: Session = Depends(get_db)):
    corpus = corpus_crud.create_corpus(db, payload.corpus_name, payload.text)
    return {"corpus_id": corpus.id, "message": "Corpus uploaded successfully"}

@router.get("/corpuses", response_model=corpus_schema.CorpusesResponse)
def get_corpuses(db: Session = Depends(get_db)):
    corpuses = corpus_crud.get_all_corpuses(db)
    return {"corpuses": [{"id": c.id, "name": c.corpus_name} for c in corpuses]}

@router.post("/search_algorithm", response_model=search_schema.SearchResponse)
def search_algorithm(payload: search_schema.SearchRequest, db: Session = Depends(get_db)):
    # Получаем корпус по идентификатору
    corpus = corpus_crud.get_corpus_by_id(db, payload.corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")
    
    # Разбиваем текст корпуса на слова (простая токенизация)
    words = corpus.text.split()
    
    # Выбираем алгоритм для нечеткого поиска
    if payload.algorithm.lower() == "levenshtein":
        algorithm_func = fuzzy_search.levenshtein
    elif payload.algorithm.lower() == "damerau_levenshtein":
        algorithm_func = fuzzy_search.damerau_levenshtein
    else:
        raise HTTPException(status_code=400, detail="Unknown algorithm")
    
    # Замер времени выполнения алгоритма
    start_time = time.time()
    results = []
    for word in words:
        distance = algorithm_func(payload.word, word)
        results.append({"word": word, "distance": distance})
    execution_time = time.time() - start_time

    # Сортируем результаты по расстоянию
    results = sorted(results, key=lambda x: x["distance"])
    return {"execution_time": execution_time, "results": results}
