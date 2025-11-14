from logging import getLogger

from app.database import Course, User, UserCourse, get_session
from app.middleware import require_employee
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select

logger = getLogger(__name__)


class LearningResource(Resource):
    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):

        try:
            user_id = current_user.id

            personalized = session.exec(
                select(UserCourse, Course)
                .join(Course, Course.id == UserCourse.course_id)
                .where(UserCourse.user_id == user_id)
            ).all()

            personalized_list = []
            for uc, course in personalized:
                personalized_list.append(
                    {
                        "course_id": course.id,
                        "course_name": course.course_name,
                        "course_link": course.course_link,
                        "topics": course.topics,
                        "status": uc.status.value,
                    }
                )

            enrolled_course_ids = {uc.course_id for uc, c in personalized}

            recommended_courses = session.exec(
                select(Course).where(Course.id.not_in(enrolled_course_ids))
            ).all()

            recommended_list = [
                {
                    "course_id": c.id,
                    "course_name": c.course_name,
                    "topics": c.topics,
                    "course_link": c.course_link,
                }
                for c in recommended_courses
            ]

            return {
                "message": "Learning dashboard loaded successfully",
                "personalized": personalized_list,
                "recommended": recommended_list,
            }

        except Exception as e:
            logger.error(f"Learning page error: {e}", exc_info=True)
            raise HTTPException(500, "Internal server error")
