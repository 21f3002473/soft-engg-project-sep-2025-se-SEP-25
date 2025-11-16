# app/api/resources/hr/__init__.py
from .hr_employee_resource import EmployeeDetailResource, EmployeeListResource
from .hr_policy_resource import HRPolicyCollectionResource, HRPolicyDetailResource
from .hr_review_resource import (
    HRReviewDetailResource,
    HRReviewsByUserResource,
    HRReviewsListResource,
)

__all__ = [
    "HRReviewsListResource",
    "HRReviewsByUserResource",
    "HRReviewDetailResource",
    "HRPolicyCollectionResource",
    "HRPolicyDetailResource",
    "EmployeeListResource",
    "EmployeeDetailResource",
]
