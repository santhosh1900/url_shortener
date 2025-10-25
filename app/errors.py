class InvalidDataError(Exception):
    def __init__(self, reason=""):
        self.message = reason
        super().__init__(self.message)

class DataNotFoundError(Exception):
    def __init__(self, reason=""):
        self.message = reason
        super().__init__(self.message)

class AlreadyExistError(Exception):
    def __init__(self, reason=""):
        self.message = reason
        super().__init__(self.message)