from app.agents.hr.ask_questions import answer_question
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi_restful import Resource
from app.api.validators.hr import QuestionRequest

class AIAssistantResource(Resource):
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
            answer = answer_question(question, top_k=data.top_k)
            return JSONResponse(content={"answer": answer})
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to process question: {str(e)}"},
            )
