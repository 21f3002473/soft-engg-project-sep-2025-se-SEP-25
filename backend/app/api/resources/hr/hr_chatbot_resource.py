from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi_restful import Resource
from pydantic import BaseModel

from app.agents.hr.ask_chatbot import answer_question

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5  # included for compatibility, not used here

class HRChatbotResource(Resource):
    async def post(self, request: Request):
        body = await request.json()
        try:
            data = QuestionRequest(**body)
        except Exception:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request format. Use {'question': '...'}"},
            )

        question = data.question.strip()
        if not question:
            return JSONResponse(
                status_code=400,
                content={"error": "Question cannot be empty."},
            )

        try:
            answer = answer_question(question)
            return JSONResponse(content={"answer": answer})
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to process question: {str(e)}"},
            )

