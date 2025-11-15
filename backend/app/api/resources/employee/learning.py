from logging import getLogger

import httpx
import json

from sqlmodel import Session, select

from fastapi import Depends, HTTPException
from fastapi_restful import Resource

from app.config import Config
from app.middleware import require_employee, require_hr
from app.database import Course, User, UserCourse, get_session, StatusTypeEnum

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


class CourseAdminListCreateResource(Resource):

    def get(
        self,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Get all courses"""

        courses = session.exec(select(Course).order_by(Course.id.desc())).all()

        return [
            {
                "id": c.id,
                "course_name": c.course_name,
                "course_link": c.course_link,
                "topics": c.topics,
            }
            for c in courses
        ]

    def post(
        self,
        data: dict,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Create a new course"""

        name = data.get("course_name")
        if not name:
            raise HTTPException(400, "course_name is required")

        new_course = Course(
            course_name=name,
            course_link=data.get("course_link"),
            topics=data.get("topics"),
        )

        session.add(new_course)
        session.commit()
        session.refresh(new_course)

        return {"message": "Course created", "id": new_course.id}


class CourseAdminDetailResource(Resource):

    def get(
        self,
        course_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Get a specific course"""

        course = session.get(Course, course_id)
        if not course:
            raise HTTPException(404, "Course not found")

        return {
            "id": course.id,
            "course_name": course.course_name,
            "course_link": course.course_link,
            "topics": course.topics,
        }

    def put(
        self,
        course_id: int,
        data: dict,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Update a course"""

        course = session.get(Course, course_id)
        if not course:
            raise HTTPException(404, "Course not found")

        if "course_name" in data:
            course.course_name = data["course_name"]
        if "course_link" in data:
            course.course_link = data["course_link"]
        if "topics" in data:
            course.topics = data["topics"]

        session.commit()
        session.refresh(course)

        return {"message": "Course updated"}

    def delete(
        self,
        course_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Delete a course"""

        course = session.get(Course, course_id)
        if not course:
            raise HTTPException(404, "Course not found")

        session.delete(course)
        session.commit()

        return {"message": "Course deleted"}


class CourseAssignmentListResource(Resource):

    def get(
        self,
        user_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Get list of courses assigned to a specific user"""

        assigned = session.exec(
            select(UserCourse).where(UserCourse.user_id == user_id)
        ).all()

        return [
            {
                "id": uc.id,
                "course_id": uc.course_id,
                "course_name": uc.course.course_name if uc.course else None,
                "status": uc.status.value,
            }
            for uc in assigned
        ]

    def post(
        self,
        user_id: int,
        data: dict,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Assign a course to a user"""

        course_id = data.get("course_id")

        if not user_id or not course_id:
            raise HTTPException(400, "user_id and course_id required")

        exists = session.exec(
            select(UserCourse)
            .where(UserCourse.user_id == user_id)
            .where(UserCourse.course_id == course_id)
        ).first()

        if exists:
            raise HTTPException(400, "Course already assigned to this user")

        uc = UserCourse(
            user_id=user_id,
            course_id=course_id,
            status=StatusTypeEnum.PENDING,
        )

        session.add(uc)
        session.commit()
        session.refresh(uc)

        return {"message": "Course assigned", "id": uc.id}


class CourseAssignmentDetailResource(Resource):

    def get(
        self,
        assign_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Get details of a specific assignment"""

        uc = session.get(UserCourse, assign_id)
        if not uc:
            raise HTTPException(404, "Assignment not found")

        return {
            "id": uc.id,
            "user_id": uc.user_id,
            "course_id": uc.course_id,
            "course_name": uc.course.course_name if uc.course else None,
            "status": uc.status.value,
        }

    def put(
        self,
        assign_id: int,
        data: dict,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Update assignment"""

        uc = session.get(UserCourse, assign_id)
        if not uc:
            raise HTTPException(404, "Assignment not found")

        if "status" in data:
            status = data["status"]
            if status not in ["pending", "completed"]:
                raise HTTPException(400, "Invalid status")
            uc.status = StatusTypeEnum(status)

        if "course_id" in data:
            uc.course_id = data["course_id"]

        session.commit()
        session.refresh(uc)

        return {"message": "Assignment updated"}

    def delete(
        self,
        assign_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """HR: Remove course assignment"""

        uc = session.get(UserCourse, assign_id)
        if not uc:
            raise HTTPException(404, "Assignment not found")

        session.delete(uc)
        session.commit()

        return {"message": "Assignment removed"}


class CourseAssignmentEmployeeResource(Resource):

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """Employee: Get their own course assignments"""

        assigned = session.exec(
            select(UserCourse).where(UserCourse.user_id == current_user.id)
        ).all()

        return [
            {
                "id": uc.id,
                "course_id": uc.course_id,
                "course_name": uc.course.course_name if uc.course else None,
                "status": uc.status.value,
            }
            for uc in assigned
        ]


class CourseRecommendationResource(Resource):

    async def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Recommend courses using Gemini based on assigned courses.
        """

        try:
            user_id = current_user.id

            assigned = session.exec(
                select(UserCourse).where(UserCourse.user_id == user_id)
            ).all()

            assigned_course_ids = [uc.course_id for uc in assigned]

            assigned_course_names = [
                session.get(Course, cid).course_name
                for cid in assigned_course_ids
                if session.get(Course, cid)
            ]
            
            courses = session.exec(select(Course)).all()

            all_course_names = [c.course_name for c in courses]

            prompt = f"""
            A user has completed or is assigned these courses: {assigned_course_names}.
            The full list of available courses is: {all_course_names}.

            Based on similarity, difficulty, or natural learning progression…

            → Recommend EXACT course names from the available list.
            → Return ONLY a JSON list. Example:
            ["Machine Learning", "Deep Learning Basics"]
            """

            GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    GEMINI_URL,
                    params={"key": Config.GEMINI_API_KEY},
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                )

            if response.status_code != 200:
                logger.error(response.text)
                raise HTTPException(500, "Gemini API request failed")

            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

            try:
                recommended_names = json.loads(text)
            except:
                recommended_names = [name for name in all_course_names if name in text]

            final_recommendations = [
                {
                    "id": c.id,
                    "course_name": c.course_name,
                    "course_link": c.course_link,
                    "topics": c.topics,
                }
                for c in courses
                if c.course_name in recommended_names
            ]

            return {
                "assigned_courses": assigned_course_names,
                "recommended_courses": final_recommendations,
            }

        except Exception as e:
            logger.error(f"Recommendation error: {e}", exc_info=True)
            raise HTTPException(500, "Internal server error")
