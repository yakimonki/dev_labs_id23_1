from pydantic import BaseModel
from typing import List

class UploadCorpusRequest(BaseModel):
    corpus_name: str
    text: str

class UploadCorpusResponse(BaseModel):
    corpus_id: int
    message: str

class CorpusItem(BaseModel):
    id: int
    name: str

class CorpusesResponse(BaseModel):
    corpuses: List[CorpusItem]

