from app.database import Project, User, engine
from app.middleware import require_hr, require_pm, require_root
from fastapi import Depends
from fastapi_restful import Resource
from sqlmodel import Session, select


class HRProjectListResource(Resource):
    def get(self):
        """
        Returns:
        [
            {
                "name": <project_name>,
                "manager": <manager_name or 'Not Assigned'>
            }
        ]
        """

        with Session(engine) as session:
            stmt = select(Project)
            projects = session.exec(stmt).all()

            result = []
            for p in projects:
                manager_name = None
                if p.manager_id:
                    manager = session.get(User, p.manager_id)
                    manager_name = manager.name if manager else None

                result.append(
                    {
                        "name": p.project_name,
                        "manager": manager_name or "Not Assigned",
                    }
                )

            return {"projects": result}
