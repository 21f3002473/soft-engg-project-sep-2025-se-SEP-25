from logging import getLogger

import httpx
from app.api.validators import ChatMessage, ChatResponse
from app.config import Config
from app.database import User, get_session
from app.middleware import require_employee
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session

logger = getLogger(__name__)


class AIAssistantResource(Resource):

    async def post(
        self,
        payload: ChatMessage,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """AI assistant chat endpoint (Gemini version)"""

        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                "gemini-2.0-flash:generateContent"
                f"?key={Config.GEMINI_API_KEY}"
            )

            body = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": f"You are Sync'em AI Assistant.\nUser: {payload.message}"
                            }
                        ],
                    }
                ]
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    url, headers={"Content-Type": "application/json"}, json=body
                )

            if res.status_code != 200:
                logger.error(res.text)
                raise HTTPException(500, "LLM request failed")

            data = res.json()

            reply = data["candidates"][0]["content"]["parts"][0]["text"]

            return ChatResponse(reply=reply)

        except Exception as e:
            logger.error("AI Assistant Error", exc_info=True)
            raise HTTPException(500, "Internal server error")
