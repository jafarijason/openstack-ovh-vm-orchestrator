"""
Exception hierarchy for OpenStack VM Orchestrator.

All custom exceptions inherit from OrchestratorException for easy catching and handling.
"""


class OrchestratorException(Exception):
    """Base exception for all orchestrator errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        """Initialize orchestrator exception.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (e.g., "VM_NOT_FOUND")
            status_code: HTTP status code to return (default 500)
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(OrchestratorException):
    """Raised when input validation fails."""

    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        super().__init__(message, code, status_code=400)


class NotFoundError(OrchestratorException):
    """Raised when a resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(message, code=f"{resource_type.upper()}_NOT_FOUND", status_code=404)


class ConflictError(OrchestratorException):
    """Raised when an operation conflicts with existing state."""

    def __init__(self, message: str, code: str = "CONFLICT"):
        super().__init__(message, code, status_code=409)


class OperationNotAllowedError(OrchestratorException):
    """Raised when an operation is not allowed in current state."""

    def __init__(self, operation: str, current_state: str):
        message = f"Cannot {operation}: VM is {current_state}"
        super().__init__(message, code="OPERATION_NOT_ALLOWED", status_code=409)


class CloudConnectionError(OrchestratorException):
    """Raised when unable to connect to OpenStack cloud."""

    def __init__(self, cloud_name: str, reason: str):
        message = f"Failed to connect to cloud '{cloud_name}': {reason}"
        super().__init__(message, code="CLOUD_CONNECTION_ERROR", status_code=503)


class CloudOperationError(OrchestratorException):
    """Raised when a cloud operation fails."""

    def __init__(self, operation: str, reason: str):
        message = f"Cloud operation '{operation}' failed: {reason}"
        super().__init__(message, code="CLOUD_OPERATION_ERROR", status_code=500)


class InsufficientResourcesError(OrchestratorException):
    """Raised when cloud is out of resources."""

    def __init__(self, reason: str):
        super().__init__(reason, code="INSUFFICIENT_RESOURCES", status_code=503)


class UnauthorizedError(OrchestratorException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, code="UNAUTHORIZED", status_code=401)


class ForbiddenError(OrchestratorException):
    """Raised when user lacks permissions."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, code="FORBIDDEN", status_code=403)
