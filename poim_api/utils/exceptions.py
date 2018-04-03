from rest_framework.exceptions import *  # для упрощения импорта стандартных исключений
from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Conflict'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail


class Gone(APIException):
    status_code = status.HTTP_410_GONE
    default_detail = 'Gone'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail


class InternalServerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Internal Server Error'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail
