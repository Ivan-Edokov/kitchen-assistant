from rest_framework import exceptions, status


class CustomApiException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail, status_code):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code
