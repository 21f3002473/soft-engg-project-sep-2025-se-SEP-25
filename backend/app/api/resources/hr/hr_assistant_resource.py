from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi_restful import Resource
from pydantic import BaseModel

# Import the existing function from your agent
from app.agents.hr.ask_questions import answer_question

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5  # optional


class AIAssistantResource(Resource):
    """
    HR AI Assistant Resource
    """

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
            # Call the imported function
            answer = answer_question(question, top_k=data.top_k)

            # If your function prints instead of returning, you need to modify ask_questions.py:
            # Replace `print(resp.text)` with `return resp.text` in answer_question.
            return JSONResponse(content={"answer": answer})
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to process question: {str(e)}"},
            )
