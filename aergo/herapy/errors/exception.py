# -*- coding: utf-8 -*-

import inspect


class AergoException(Exception):
    # Exception types
    Comm = "Communication Exception"
    Conv = "Conversion Exception"
    General = "General Exception"

    def __init__(self, error, exception_type):
        self.error = error
        self.exception_type = exception_type

    def __str__(self):
        print_err = "{0} : {1}".format(self.exception_type, self.error)

        return print_err


class CommunicationException(AergoException):
    def __init__(self, error):
        if hasattr(error, 'code') and inspect.isfunction(error.code):
            self.error_code = error.code()
        if hasattr(error, 'details') and inspect.isfunction(error.details):
            self.error_details = error.details()
        self.exception_type = AergoException.Comm

    def __str__(self):
        print_err = "{0} ({1}): {2}".format(self.exception_type, self.error_code, self.error_details)

        return print_err


"""
Use this code when you add another module's exception.
You can see AergoException's print(__str__) format by using only this code.
If you want another format make __str__ like CommunicationException.

class TestException(AergoException):
    def __init__(self, error):
        super().__init__(error, EXCEPTION_TYPE)

"""
