# app/api/resources/hr/__init__.py
from .hr_review_resource import HRReviewsListResource, HRReviewsByUserResource, HRReviewDetailResource
from .hr_policy_resource import HRPolicyCollectionResource, HRPolicyDetailResource
from .hr_employee_resource import EmployeeListResource, EmployeeDetailResource

__all__ = [
    "HRReviewsListResource",
    "HRReviewsByUserResource",
    "HRReviewDetailResource",
    "HRPolicyCollectionResource",
    "HRPolicyDetailResource",
    "EmployeeListResource",
    "EmployeeDetailResource",
]
