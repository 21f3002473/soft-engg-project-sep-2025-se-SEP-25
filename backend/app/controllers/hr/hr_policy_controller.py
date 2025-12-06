from typing import Any, Dict, List

from app.database.hr_models import HRPolicy
from fastapi import HTTPException
from sqlmodel import Session, select


def get_policies(session: Session) -> List[HRPolicy]:
    return session.exec(select(HRPolicy).order_by(HRPolicy.created_at.desc())).all()


def get_policy(policy_id: int, session: Session) -> HRPolicy:
    policy = session.get(HRPolicy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


def create_policy(payload: Dict[str, Any], session: Session) -> HRPolicy:
    policy = HRPolicy(title=payload["title"], content=payload["content"])
    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy


def update_policy(
    policy_id: int, payload: Dict[str, Any], session: Session
) -> HRPolicy:
    policy = session.get(HRPolicy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if "title" in payload:
        policy.title = payload["title"]
    if "content" in payload:
        policy.content = payload["content"]

    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy


def delete_policy(policy_id: int, session: Session) -> dict:
    policy = session.get(HRPolicy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    session.delete(policy)
    session.commit()
    return {"message": "Policy deleted"}
