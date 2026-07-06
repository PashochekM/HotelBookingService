class AppError(Exception):
    default_message = "Application error"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class ObjectNotFoundError(AppError):
    default_message = "Object not found"


class ObjectAlreadyExistsError(AppError):
    default_message = "Object already exists"


class RelatedObjectNotFoundError(AppError):
    default_message = "Related object not found"


class DatabaseIntegrityError(AppError):
    default_message = "Database integrity error"


class RoomNotAvailableError(AppError):
    default_message = "Room is not available for the selected dates"


class InvalidBookingDatesError(AppError):
    default_message = "date_to must be later than date_from"


class InvalidCredentialsError(AppError):
    default_message = "Incorrect email or password"


class InvalidTokenError(AppError):
    default_message = "Invalid token"


class ForbiddenError(AppError):
    default_message = "Forbidden"


class TokenExpiredError(AppError):
    default_message = "Token has expired"


class InvalidImageError(AppError):
    default_message = "Invalid image"


class InfrastructureError(AppError):
    default_message = "Infrastructure error"
