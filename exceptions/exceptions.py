class NoMoreBusError(Exception):
    def __init__(self, message="No more bus liao :("):
        super().__init__(message)


class NoSearchResultsError(Exception):
    def __init__(self, message="No search results match the query"):
        super().__init__(message)


class InvalidCommandError(Exception):
    def __init__(self, message="Invalid command 😯"):
        super().__init__(message)


class APIError(Exception):
    def __init__(self, response_status_code=None, message="Error occurred."):
        super().__init__(message)
        self.response_status_code = response_status_code

    def __str__(self):
        if self.response_status_code:
            return f"{self.message} Response status code: {self.response_status_code}"
        else:
            return self.message


class InvalidCallbackDataError(Exception):
    def __init__(self, message="Invalid callback data"):
        super().__init__(message)
