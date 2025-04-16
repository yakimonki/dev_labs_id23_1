import time
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

#Команды которые нужно прописать в терминале

#pip install fastapi "uvicorn[standard]"

#pip install python-Levenshtein

#Команда для запуска

#uvicorn main:app --reload

try:
    import Levenshtein
    def calculate_levenshtein(word1: str, word2: str) -> int:
        return Levenshtein.distance(word1, word2)

    def calculate_damerau_levenshtein(word1: str, word2: str) -> int:

        return Levenshtein.distance(word1, word2, weights=(1, 1, 1, 1))


except ImportError:
    print("WARN: Levenshtein library not found. Using basic pure Python implementations (slower).")
    print("Install it: pip install python-Levenshtein")


    def calculate_levenshtein(s1, s2):
        if len(s1) < len(s2):
            return calculate_levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]


    def calculate_damerau_levenshtein(word1: str, word2: str) -> int:
        print("WARN: Damerau-Levenshtein requires the 'python-Levenshtein' library or a complex manual implementation.")

        return calculate_levenshtein(word1, word2)



corpuses_storage: Dict[int, Dict] = {}
next_corpus_id: int = 1



class CorpusUploadRequest(BaseModel):
    corpus_name: str
    text: str

class CorpusUploadResponse(BaseModel):
    corpus_id: int
    message: str

class CorpusInfo(BaseModel):
    id: int
    name: str

class CorpusListResponse(BaseModel):
    corpuses: List[CorpusInfo]

class SearchRequest(BaseModel):
    word: str
    algorithm: str
    corpus_id: int
    max_distance: Optional[int] = None

class SearchResultItem(BaseModel):
    word: str
    distance: int

class SearchResponse(BaseModel):
    execution_time: float
    results: List[SearchResultItem]

# --- Создание FastAPI приложения ---
app = FastAPI(title="Fuzzy Search API")


def tokenize_and_clean(text: str) -> List[str]:

    text = text.lower()

    text = re.sub(r'[^\w\s]', '', text)

    words = text.split()

    words = [word for word in words if word]

    return list(set(words))



@app.post("/upload_corpus", response_model=CorpusUploadResponse)
async def upload_corpus(request: CorpusUploadRequest):
    """
    Загружает корпус текста для индексации и поиска.
    """
    global next_corpus_id
    corpus_id = next_corpus_id

    words = tokenize_and_clean(request.text)


    corpuses_storage[corpus_id] = {
        "name": request.corpus_name,
        "words": words
    }
    next_corpus_id += 1

    return CorpusUploadResponse(
        corpus_id=corpus_id,
        message="Corpus uploaded successfully"
    )

@app.get("/corpuses", response_model=CorpusListResponse)
async def get_corpuses():
    """
    Возвращает список загруженных корпусов c идентификаторами.
    """
    corpus_list = [
        CorpusInfo(id=cid, name=data["name"])
        for cid, data in corpuses_storage.items()
    ]
    return CorpusListResponse(corpuses=corpus_list)

@app.post("/search_algorithm", response_model=SearchResponse)
async def search_algorithm(request: SearchRequest):
    """
    Выполняет нечеткий поиск слова в указанном корпусе
    с использованием выбранного алгоритма.
    """

    if request.corpus_id not in corpuses_storage:
        raise HTTPException(status_code=404, detail=f"Corpus with id {request.corpus_id} not found")

    corpus_data = corpuses_storage[request.corpus_id]
    corpus_words = corpus_data["words"]
    search_word = request.word.lower()


    if request.algorithm == "levenshtein":
        distance_func = calculate_levenshtein
    elif request.algorithm == "damerau_levenshtein":
        distance_func = calculate_damerau_levenshtein
    else:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {request.algorithm}. Available: levenshtein, damerau_levenshtein")


    start_time = time.time()
    results = []
    for corpus_word in corpus_words:
        distance = distance_func(search_word, corpus_word)

        if request.max_distance is None or distance <= request.max_distance:
            results.append(SearchResultItem(word=corpus_word, distance=distance))

    end_time = time.time()
    execution_time = end_time - start_time


    results.sort(key=lambda item: item.distance)

    return SearchResponse(
        execution_time=execution_time,
        results=results
    )


@app.get("/")
async def read_root():
    return {"message": "Fuzzy Search API is running. Go to /docs for documentation."}