import json
from logging import getLogger

import httpx
from app.config import Config
from app.database import Course, StatusTypeEnum, User, UserCourse, get_session
from app.middleware import require_employee, require_hr
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select

logger = getLogger(__name__)


class LearningResource(Resource):
    """
    Employee Learning Dashboard Resource - Story Points:
    - "As an Employee, I want to search for and view a list of skill improvement and learning courses..."
    - "As an Employee, I want GenAI to give me personalised recommendations for skill improvement..."

    Provides a consolidated view of employee's personalized learning path. Displays courses
    the employee is enrolled in alongside recommended courses not yet taken. This enables
    employees to track their learning progress and discover relevant skill-building opportunities.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve personalized learning dashboard with enrolled and recommended courses.

        Story Points Supported:
        - "As an Employee, I want to search for and view a list of skill improvement and learning courses so that I can choose the ones that help me grow..."
        - "As an Employee, I want GenAI to give me personalised recommendations for skill improvement..."

        Aggregates:
        1. Personalized Courses: Courses the employee is currently enrolled in with their status
        2. Recommended Courses: Courses available but not yet enrolled in

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session for querying

        Returns:
            dict: Learning dashboard data containing:
                - message (str): "Learning dashboard loaded successfully"
                - personalized (list[dict]): Courses the employee is enrolled in, each containing:
                    - course_id (int): Unique course identifier
                    - course_name (str): Name of the course
                    - course_link (str): URL/link to course resources
                    - topics (str): Comma-separated topics covered in course
                    - status (str): "pending" (in-progress) or "completed"
                - recommended (list[dict]): Available courses not yet enrolled, each containing:
                    - course_id (int): Unique course identifier
                    - course_name (str): Name of the course
                    - topics (str): Topics covered
                    - course_link (str): URL/link to course resources

        Error Codes:
            - 500 Internal Server Error: Database query failures or session errors

        Raises:
            HTTPException(500): If any database operation fails during aggregation
        """

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
    """
    HR Course Management Resource (List/Create) - Story Point:
    "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

    Allows HR personnel to manage the course catalog. HR can create new courses, view all available
    courses, and manage course metadata. This enables HR to curate a relevant skill-development
    catalog for employee growth.
    """

    def get(
        self,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all available courses in the system (HR only).

        Story Points Supported:
        - "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

        Args:
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            list[dict]: Array of all courses, each containing:
                - id (int): Course identifier
                - course_name (str): Name of the course
                - course_link (str): URL/link to course resources
                - topics (str): Topics covered in the course

        Error Codes:
            - 401 Unauthorized: User is not HR personnel (caught by middleware)
        """

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
        """
        Create a new course in the system (HR only).

        Story Points Supported:
        - "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

        Args:
            data (dict): Request payload containing:
                - course_name (str, required): Name of the course
                - course_link (str, optional): URL/link to course resources
                - topics (str, optional): Comma-separated topics covered
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation with new course details
                - message (str): "Course created"
                - id (int): ID of newly created course

        Error Codes:
            - 400 Bad Request: Missing required "course_name" field
            - 401 Unauthorized: User is not HR personnel
        """

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
    """
    HR Course Detail Operations - Story Point:
    "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

    Handles retrieval, update, and deletion of individual courses by HR personnel.
    Enables HR to modify course information and remove outdated courses from the catalog.
    """

    def get(
        self,
        course_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve details of a specific course (HR only).

        Args:
            course_id (int): The ID of the course to retrieve
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Course details
                - id (int): Course identifier
                - course_name (str): Name of the course
                - course_link (str): URL/link to course resources
                - topics (str): Topics covered

        Error Codes:
            - 404 Not Found: Course with given ID does not exist
            - 401 Unauthorized: User is not HR personnel
        """

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
        """
        Update an existing course (HR only).

        Args:
            course_id (int): The ID of the course to update
            data (dict): Request payload with optional fields:
                - course_name (str, optional): Updated course name
                - course_link (str, optional): Updated course URL
                - topics (str, optional): Updated topics list
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Course updated"

        Error Codes:
            - 404 Not Found: Course does not exist
            - 401 Unauthorized: User is not HR personnel
        """

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
        """
        Delete a course from the system (HR only).

        Args:
            course_id (int): The ID of the course to delete
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Course deleted"

        Error Codes:
            - 404 Not Found: Course does not exist
            - 401 Unauthorized: User is not HR personnel
        """

        course = session.get(Course, course_id)
        if not course:
            raise HTTPException(404, "Course not found")

        session.delete(course)
        session.commit()

        return {"message": "Course deleted"}


class CourseAssignmentListResource(Resource):
    """
    HR Course Assignment Management (List/Create) - Story Point:
    "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

    Allows HR to assign/enroll courses to specific employees. HR can view all courses assigned
    to an employee and create new assignments. This enables targeted skill-development planning
    based on employee roles and career paths.
    """

    def get(
        self,
        user_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve list of courses assigned to a specific employee (HR only).

        Args:
            user_id (int): The employee ID to fetch assignments for
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            list[dict]: Array of course assignments, each containing:
                - id (int): Assignment ID
                - course_id (int): Course identifier
                - course_name (str): Name of the assigned course
                - status (str): "pending" (in-progress) or "completed"

        Error Codes:
            - 401 Unauthorized: User is not HR personnel
        """

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
        """
        Assign a course to an employee (HR only).

        Story Points Supported:
        - "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

        Args:
            user_id (int): The employee ID to assign course to
            data (dict): Request payload containing:
                - course_id (int, required): The course to assign
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation with assignment details
                - message (str): "Course assigned"
                - id (int): Assignment ID

        Error Codes:
            - 400 Bad Request: Missing user_id or course_id, or course already assigned to user
            - 401 Unauthorized: User is not HR personnel
        """

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
    """
    HR Course Assignment Detail Operations - Story Point:
    "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

    Handles retrieval, update, and removal of individual course assignments by HR personnel.
    Enables HR to track assignment status and modify or cancel assignments as needed.
    """

    def get(
        self,
        assign_id: int,
        current_user: User = Depends(require_hr()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve details of a specific course assignment (HR only).

        Args:
            assign_id (int): The ID of the assignment to retrieve
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Assignment details
                - id (int): Assignment identifier
                - user_id (int): Employee ID
                - course_id (int): Course identifier
                - course_name (str): Name of the course
                - status (str): "pending" or "completed"

        Error Codes:
            - 404 Not Found: Assignment does not exist
            - 401 Unauthorized: User is not HR personnel
        """

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
        """
        Update a course assignment (HR only). Can modify status or course assignment.

        Args:
            assign_id (int): The ID of the assignment to update
            data (dict): Request payload with optional fields:
                - status (str, optional): Must be "pending" or "completed"
                - course_id (int, optional): Reassign to a different course
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Assignment updated"

        Error Codes:
            - 404 Not Found: Assignment does not exist
            - 400 Bad Request: Invalid status value
            - 401 Unauthorized: User is not HR personnel
        """

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
        """
        Remove a course assignment from an employee (HR only).

        Args:
            assign_id (int): The ID of the assignment to remove
            current_user (User): Authenticated HR user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Assignment removed"

        Error Codes:
            - 404 Not Found: Assignment does not exist
            - 401 Unauthorized: User is not HR personnel
        """

        uc = session.get(UserCourse, assign_id)
        if not uc:
            raise HTTPException(404, "Assignment not found")

        session.delete(uc)
        session.commit()

        return {"message": "Assignment removed"}


class CourseAssignmentEmployeeResource(Resource):
    """
    Employee Course Assignment Viewing - Story Point:
    "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

    Read-only endpoint for employees to view their assigned courses. Enables employees to see
    which courses have been assigned to them by HR and track their enrollment status.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve all courses assigned to the logged-in employee.

        Story Points Supported:
        - "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            list[dict]: Array of assigned courses, each containing:
                - id (int): Assignment ID
                - course_id (int): Course identifier
                - course_name (str): Name of the assigned course
                - status (str): "pending" (in-progress) or "completed"

        Error Codes:
            - 401 Unauthorized: User is not an employee (caught by middleware)
        """

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
    """
    GenAI-Powered Course Recommendation Resource - Story Points:
    - "As an Employee, I want GenAI to give me personalised recommendations for skill improvement..."
    - "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

    Uses Google Gemini GenAI to analyze employee's current course enrollment and recommend
    relevant next courses for skill development. Recommendations are based on learning progression,
    course similarity, and career development paths. This enables personalized, data-driven
    learning recommendations without manual HR curation.
    """

    async def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Generate personalized course recommendations using GenAI (Gemini).

        Story Points Supported:
        - "As an Employee, I want GenAI to give me personalised recommendations for skill improvement..."
        - "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

        Workflow:
        1. Fetch employee's currently assigned/completed courses
        2. Send course list and available catalog to Gemini API
        3. Request similar/progressive course recommendations
        4. Parse GenAI response and match to actual courses in database
        5. Return recommendations with full course details

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Recommendations data containing:
                - assigned_courses (list[str]): Names of courses employee is already taking
                - recommended_courses (list[dict]): GenAI-recommended courses, each with:
                    - id (int): Course identifier
                    - course_name (str): Name of the course
                    - course_link (str): URL/link to course resources
                    - topics (str): Topics covered

        Error Codes:
            - 500 Internal Server Error: GenAI API failures, database issues, JSON parsing errors
            - 503 Service Unavailable: GenAI API request timeout or service unavailable

        Raises:
            HTTPException(500): If Gemini API request fails or response parsing fails

        GenAI Integration:
            - Uses Google Gemini 2.0 Flash model for fast, personalized recommendations
            - Sends current course list and full catalog to AI for analysis
            - Requests course names matching available catalog to ensure valid results
            - Falls back to text-search matching if JSON parsing fails
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

            GEMINI_URL = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                "gemini-2.5-flash:generateContent"
            )

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


class EmployeeCourseUpdateByCourseIdResource(Resource):
    """
    Employee Course Status Update Resource - Story Point:
    "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

    Allows employees to update the status of their assigned courses (mark as pending/completed).
    Enables employees to track their learning progress independently. This supports the story of
    monitoring course completion and documenting skill development.
    """

    def put(
        self,
        course_id: int,
        data: dict,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Update the status of an assigned course (using course_id).

        Story Points Supported:
        - "As an Employee, I want to search for and view a list of skill improvement and learning courses..."

        Args:
            course_id (int): The course ID to update status for
            data (dict): Request payload containing:
                - status (str, required): Must be "pending" or "completed"
            current_user (User): Authenticated employee user object
            session (Session): Database session

        Returns:
            dict: Confirmation message
                - message (str): "Course status updated"

        Error Codes:
            - 404 Not Found: Course assignment does not exist for this employee
            - 400 Bad Request: Missing "status" field or invalid status value
            - 401 Unauthorized: User is not an employee
        """

        uc = session.exec(
            select(UserCourse)
            .where(UserCourse.user_id == current_user.id)
            .where(UserCourse.course_id == course_id)
        ).first()

        if not uc:
            raise HTTPException(404, "Course assignment not found")

        if "status" not in data:
            raise HTTPException(400, "status field is required")

        status = data["status"]
        if status not in ["pending", "completed"]:
            raise HTTPException(400, "Invalid status")

        uc.status = StatusTypeEnum(status)

        session.commit()
        session.refresh(uc)

        return {"message": "Course status updated"}
