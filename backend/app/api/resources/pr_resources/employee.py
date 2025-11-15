from logging import getLogger

from app.database import User, get_session
from app.database.product_manager_models import EmpTodo, StatusTypeEnum
from app.middleware import require_pm
from fastapi import Depends, HTTPException
from fastapi_restful import Resource
from sqlmodel import Session, select, func

logger = getLogger(__name__)


class EmployeesResource(Resource):
    """
    Resource for managing employee data.

    This resource provides endpoints for retrieving employee information.
    Only project managers (PM) are authorized to access these endpoints.

    Attributes:
        None

    Methods:
        get: Retrieve all employees in the system with their basic information.
    """
    def get(
        self,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Get all employees"""
        try:
            logger.info(f"Fetching all employees by {current_user.email}")

            # Query all users (employees)
            statement = select(User).where(User.role == 'employee')
            employees = session.exec(statement).all()

            # Format employee data
            employee_list = [
                {
                    "id": emp.id,
                    "name": emp.name,
                    "email": emp.email,
                    "role": emp.role,
                }
                for emp in employees
            ]

            return {
                "message": "Employees retrieved successfully",
                "data": {
                    "employees": employee_list,
                    "total_employees": len(employee_list),
                },
            }

        except Exception as e:
            logger.error(f"Error fetching employees: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")


class EmployeePerformanceResource(Resource):
    """
    Resource for retrieving employee performance metrics and statistics.

    This resource provides performance data for a specific employee, including:
    - Employee basic information (id, name, email, role)
    - Current task statistics (completed, in_progress, pending, total counts and percentages)
    - Performance trends over time (monthly performance scores)

    Attributes:
        None

    Methods:
        get(employee_id, current_user, session): Retrieves performance data for a specific employee
    """
    def get(
        self,
        employee_id: int,
        current_user: User = Depends(require_pm()),
        session: Session = Depends(get_session),
    ):
        """Get performance data for a specific employee"""
        try:
            logger.info(f"Fetching performance for employee {employee_id} by {current_user.email}")

            # Query employee
            employee_statement = select(User).where(User.id == employee_id)
            employee = session.exec(employee_statement).first()

            if not employee:
                raise HTTPException(status_code=404, detail="Employee not found")

            # Query employee todos/tasks
            todo_statement = select(EmpTodo).where(EmpTodo.user_id == employee_id)
            todos = session.exec(todo_statement).all()

            # Calculate current stats
            total_tasks = len(todos)
            completed_tasks = sum(1 for t in todos if t.status == StatusTypeEnum.COMPLETED)
            in_progress_tasks = sum(1 for t in todos if t.status == StatusTypeEnum.PENDING)
            pending_tasks = total_tasks - completed_tasks - in_progress_tasks

            # Calculate percentages for pie chart
            completed_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            in_progress_percentage = (in_progress_tasks / total_tasks * 100) if total_tasks > 0 else 0
            pending_percentage = (pending_tasks / total_tasks * 100) if total_tasks > 0 else 0

            # Mock performance trend data (you can replace this with actual data from database)
            performance_trends = [
                {"month": "Jan", "score": 65},
                {"month": "Feb", "score": 72},
                {"month": "Mar", "score": 68},
                {"month": "Apr", "score": 78},
                {"month": "May", "score": 85},
                {"month": "Jun", "score": 88},
            ]

            return {
                "message": "Employee performance retrieved successfully",
                "data": {
                    "employee": {
                        "id": employee.id,
                        "name": employee.name,
                        "email": employee.email,
                        "role": employee.role,
                    },
                    "current_stats": {
                        "completed": completed_tasks,
                        "in_progress": in_progress_tasks,
                        "pending": pending_tasks,
                        "total": total_tasks,
                        "completed_percentage": round(completed_percentage, 2),
                        "in_progress_percentage": round(in_progress_percentage, 2),
                        "pending_percentage": round(pending_percentage, 2),
                    },
                    "performance_trends": performance_trends,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching employee performance: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
