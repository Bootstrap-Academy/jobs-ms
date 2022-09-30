from fastapi import status

from .api_exception import APIException


class CompanyNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Company not found"
    description = "This company does not exist."


class CompanyAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Company already exists"
    description = "A company with this name already exists."
