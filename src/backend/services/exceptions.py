class DomainError(Exception):
    """Base class for expected business errors."""


class AuthenticationError(DomainError):
    pass


class DuplicateEmailError(DomainError):
    pass


class InvalidPasswordError(DomainError):
    pass


class InvalidRefreshTokenError(DomainError):
    pass


class ConversationNotFoundError(DomainError):
    pass


class ConversationHasNoDocumentsError(DomainError):
    pass


class DocumentNotFoundError(DomainError):
    pass


class UnsupportedFileTypeError(DomainError):
    def __init__(self, valid_extensions: tuple[str, ...]):
        self.valid_extensions = valid_extensions
        super().__init__("Unsupported file type")


class UploadTooLargeError(DomainError):
    pass


class DocumentProcessingError(DomainError):
    pass
