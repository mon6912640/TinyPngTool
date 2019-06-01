# -*- coding: utf-8 -*-
class Error(Exception):
    @staticmethod
    def create(message, kind, status):
        error_class = None
        if status == 401 or status == 429:
            error_class = AccountError
        elif status >= 400 and status <= 499:
            error_class = ClientError
        elif status >= 400 and status < 599:
            error_class = ServerError
        else:
            error_class = Error

        if not message:
            message = 'No message was provided'
        return error_class(message, kind, status)

    def __init__(self, message, kind=None, status=None, cause=None):
        self.message = message
        self.kind = kind
        self.status = status
        if cause:
            # Equivalent to 'raise err from cause', also supported by Python 2.
            self.__cause__ = cause

    def __str__(self):
        if self.status:
            return '{0} (HTTP {1:d}/{2})'.format(self.message, self.status, self.kind)
        else:
            return self.message


# =======================================
class AccountError(Error):
    pass


class ClientError(Error):
    pass


class ServerError(Error):
    pass


class ConnectError(Error):
    pass
