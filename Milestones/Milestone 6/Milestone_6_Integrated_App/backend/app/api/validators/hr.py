from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5
