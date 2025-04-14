from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    word: str
    algorithm: str  # "levenshtein" или "damerau_levenshtein"
    corpus_id: int

class SearchResult(BaseModel):
    word: str
    distance: int

class SearchResponse(BaseModel):
    execution_time: float
    results: List[SearchResult]
