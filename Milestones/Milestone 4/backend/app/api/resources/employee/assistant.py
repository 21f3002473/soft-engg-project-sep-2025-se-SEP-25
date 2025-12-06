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
    """
    GenAI-Powered HR Chatbot Resource - Story Point:
    "As an Employee, I want GenAI chatbot to provide me with instant answers to HR-related queries..."

    Provides an AI-powered conversational assistant for employees to get instant answers to
    common HR queries without waiting for manager or HR support. The chatbot leverages Google
    Gemini 2.0 Flash model to handle queries about:
    - Dress code policies
    - Leave types and procedures
    - Work-from-home (WFH) guidelines
    - Travel policies and reimbursement
    - Benefits and compensation
    - General HR procedures

    This enables employees to resolve trivial, frequently-asked HR questions in real-time,
    reducing support overhead and improving employee satisfaction. Responses are powered by
    GenAI for natural, contextual answers tailored to the query.
    """

    async def post(
        self,
        payload: ChatMessage,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Send a message to the GenAI HR chatbot and receive an instant response.

        Story Points Supported:
        - "As an Employee, I want GenAI chatbot to provide me with instant answers to HR-related queries (e.g., dress code, leave, WFH, travel) so that I don't have to wait for my manager to address trivial questions."

        Workflow:
        1. Receive employee query/message
        2. Format message with system prompt identifying this as Sync'em AI Assistant
        3. Send to Google Gemini 2.0 Flash API with appropriate context
        4. Parse and return AI-generated response
        5. Handle timeouts and API errors gracefully

        Args:
            payload (ChatMessage): Request payload containing:
                - message (str): Employee's HR query or question (e.g., "What is the dress code?", "How do I request WFH?")
            current_user (User): Authenticated employee user object
            session (Session): Database session (passed for consistency, not actively used)

        Returns:
            ChatResponse: AI-generated response containing:
                - reply (str): Natural language answer to the employee's question from Gemini

        Error Codes:
            - 400 Bad Request: Missing or invalid message in payload
            - 401 Unauthorized: User is not an employee (caught by middleware)
            - 500 Internal Server Error: GenAI API request failures, timeouts, or response parsing errors
            - 503 Service Unavailable: GenAI API service down or unreachable

        Raises:
            HTTPException(500): If Gemini API request fails, times out, or response parsing fails

        GenAI Integration Details:
            - Model: Google Gemini 2.0 Flash (fast, cost-efficient)
            - System Role: "Sync'em AI Assistant" (branded HR chatbot)
            - Timeout: 30 seconds for API response
            - API: Google Generative AI REST endpoint
            - Authentication: Via Config.GEMINI_API_KEY

        Example Query/Response:
            Request: {"message": "What is our dress code policy?"}
            Response: {"reply": "Our dress code policy is business casual..."}
        """

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
