from logging import getLogger

from app.api.validators import AccountOut, AccountUpdate, SkillAddRequest, SkillUpdateRequest
from app.database import Department, User, get_session
from app.middleware import require_employee
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select
from app.database.product_manager_models import EmployeeSkill

logger = getLogger(__name__)


class AccountResource(Resource):
    """
    Employee Account Management Resource - Core Employee Profile Operations

    Manages employee account information and profile updates. Allows employees to view and
    modify their personal information including name, email, profile image, department assignment,
    and reporting manager relationship. This is a foundational resource for employee self-service
    account management across all employee-facing story points.

    Supports employee autonomy in managing their profile data and ensuring accurate HR records
    without requiring HR intervention for routine updates.
    """

    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Retrieve the logged-in employee's account profile information.

        Provides complete profile details including personal information, role, department
        assignment, and reporting structure. Department name is resolved from department_id
        for easier frontend consumption.

        Args:
            current_user (User): Authenticated employee user object
            session (Session): Database session for querying department information

        Returns:
            AccountOut: Serialized employee account information containing:
                - id (int): Unique employee identifier
                - name (str): Employee full name
                - email (str): Employee email address
                - role (str): Employee role (e.g., "employee", "product_manager", "human_resource")
                - department_id (int, optional): Department ID if assigned
                - reporting_manager (int, optional): User ID of reporting manager
                - img_base64 (str, optional): Base64-encoded profile image
                - department_name (str, optional): Human-readable department name

        Error Codes:
            - 401 Unauthorized: User is not an employee (caught by middleware)
            - 500 Internal Server Error: Database query failures or session errors

        Raises:
            HTTPException(500): If department lookup fails or database error occurs
        """
        try:
            dept_name = None

            if current_user.department_id:
                dept = session.get(Department, current_user.department_id)
                dept_name = dept.name if dept else None

            return AccountOut(
                id=current_user.id,
                name=current_user.name,
                email=current_user.email,
                role=current_user.role,
                department_id=current_user.department_id,
                reporting_manager=current_user.reporting_manager,
                img_base64=current_user.img_base64,
                department_name=dept_name,
            )
        except HTTPException:
            raise
        except Exception:
            logger.error("Account GET error", exc_info=True)
            raise HTTPException(500, "Internal server error")

    def put(
        self,
        payload: AccountUpdate,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Update the logged-in employee's account profile information.

        Allows employees to modify their personal profile data. Only fields included in the
        request payload are updated (partial updates supported). Employees can update:
        - Name and email address
        - Profile image (base64-encoded)
        - Department assignment (if available for self-assignment)
        - Reporting manager relationship (if configurable)

        Args:
            payload (AccountUpdate): Request payload with optional fields:
                - name (str, optional): Updated employee name
                - email (str, optional): Updated email address
                - img_base64 (str, optional): Base64-encoded profile image
                - department_id (int, optional): Updated department assignment
                - reporting_manager (int, optional): Updated reporting manager ID
            current_user (User): Authenticated employee user object
            session (Session): Database session for persisting updates

        Returns:
            dict: Confirmation message
                - message (str): "Account updated successfully"

        Error Codes:
            - 400 Bad Request: Invalid field values or constraint violations
            - 401 Unauthorized: User is not an employee
            - 500 Internal Server Error: Database update or commit failures

        Raises:
            HTTPException(500): If database commit fails or update operation fails
        """
        try:
            update_data = payload.model_dump(exclude_unset=True)

            user = session.merge(current_user)

            restricted = {"id", "role", "created_at"}
            if restricted & update_data.keys():
                raise HTTPException(400, "You cannot update these fields")

            for key, value in update_data.items():
                setattr(user, key, value)

            session.commit()
            session.refresh(user)

            return {"message": "Account updated successfully"}

        except HTTPException:
            raise
        except ValueError as ve:
            logger.error(ve, exc_info=True)
            raise HTTPException(400, "Invalid input data")
        except Exception as e:
            logger.error("Account Update error", exc_info=True)
            raise HTTPException(500, "Internal server error")

class EmployeeSkillListResource(Resource):
    def get(
        self,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Get the list of skills for the current logged-in employee.
        """
        try:
            skills = session.exec(
                select(EmployeeSkill).where(EmployeeSkill.employee_id == current_user.id)
            ).all()

            return [
                {
                    "id": skill.id,
                    "skill_name": skill.skill_name,
                    "proficiency_level": skill.proficiency_level,
                    "years_of_experience": skill.years_of_experience,
                    "verified": skill.verified,
                    "verified_at": skill.verified_at,
                }
                for skill in skills
            ]
        except Exception as e:
            logger.error(f"Error fetching skills: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def post(
        self,
        data: SkillAddRequest,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Add a new skill to the current logged-in employee's profile.
        """
        try:
            new_skill = EmployeeSkill(
                employee_id=current_user.id,
                skill_name=data.skill_name,
                proficiency_level=data.proficiency_level,
                years_of_experience=data.years_of_experience,
            )
            session.add(new_skill)
            session.commit()
            session.refresh(new_skill)

            return {"message": "Skill added successfully", "id": new_skill.id}
        except Exception as e:
            logger.error(f"Error adding skill: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

class EmployeeSkillDetailResource(Resource):
    def get(
        self,
        skill_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Get details of a specific skill.
        """
        try:
            skill = session.exec(
                select(EmployeeSkill).where(
                    EmployeeSkill.id == skill_id,
                    EmployeeSkill.employee_id == current_user.id
                )
            ).first()

            if not skill:
                raise HTTPException(status_code=404, detail="Skill not found")

            return {
                "id": skill.id,
                "skill_name": skill.skill_name,
                "proficiency_level": skill.proficiency_level,
                "years_of_experience": skill.years_of_experience,
                "verified": skill.verified,
                "verified_at": skill.verified_at,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching skill details: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def put(
        self,
        skill_id: int,
        data: SkillUpdateRequest,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Update a specific skill.
        """
        try:
            skill = session.exec(
                select(EmployeeSkill).where(
                    EmployeeSkill.id == skill_id,
                    EmployeeSkill.employee_id == current_user.id
                )
            ).first()

            if not skill:
                raise HTTPException(status_code=404, detail="Skill not found")

            if data.skill_name is not None:
                skill.skill_name = data.skill_name
            if data.proficiency_level is not None:
                skill.proficiency_level = data.proficiency_level
            if data.years_of_experience is not None:
                skill.years_of_experience = data.years_of_experience
            
            session.add(skill)
            session.commit()
            session.refresh(skill)

            return {"message": "Skill updated successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating skill: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def delete(
        self,
        skill_id: int,
        current_user: User = Depends(require_employee()),
        session: Session = Depends(get_session),
    ):
        """
        Delete a skill from the current logged-in employee's profile.
        """
        try:
            skill = session.exec(
                select(EmployeeSkill).where(
                    EmployeeSkill.id == skill_id,
                    EmployeeSkill.employee_id == current_user.id
                )
            ).first()

            if not skill:
                raise HTTPException(status_code=404, detail="Skill not found")

            session.delete(skill)
            session.commit()

            return {"message": "Skill deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting skill: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
