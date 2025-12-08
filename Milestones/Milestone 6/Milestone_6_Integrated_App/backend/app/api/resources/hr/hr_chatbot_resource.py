from app.agents.hr.ask_chatbot import answer_question
from app.api.validators.hr import QuestionRequest
from app.database import Chat, User, get_session
from app.middleware import require_hr
from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi_restful import Resource
from sqlmodel import Session


class HRChatbotResource(Resource):
    async def post(
        self,
        payload: QuestionRequest,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        question = payload.question.strip()
        if not question:
            return JSONResponse(
                status_code=400,
                content={"error": "Question cannot be empty."},
            )

        try:
            user_chat = Chat(
                user_id=current_user.id,
                role="user",
                message=question,
            )
            session.add(user_chat)
            session.commit()

            answer = answer_question(question)

            assistant_chat = Chat(
                user_id=current_user.id,
                role="assistant",
                message=answer,
            )
            session.add(assistant_chat)
            session.commit()

            return JSONResponse(content={"answer": answer})

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to process question: {str(e)}"},
            )
