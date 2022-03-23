class BadFileFormatError(BaseException):
    """Base class for file format errors"""


class UnknownFileFormatError(BadFileFormatError):
    """Used when a file format could not be detected"""
    pass


class WrongFileFormatError(BadFileFormatError):
    """Used when a wrong file format is used"""
    pass
