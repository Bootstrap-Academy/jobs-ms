from fastapi import status

from .api_exception import APIException


class JobNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Job not found"
    description = "This job does not exist."


class SkillNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Skill not found"
    description = "This skill does not exist."
