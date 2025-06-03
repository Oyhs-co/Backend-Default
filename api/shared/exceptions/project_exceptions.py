from typing import Any, Dict, Optional

from .base_exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)


class ProjectNotFoundException(NotFoundException):
    """Exception for project not found"""

    def __init__(
        self,
        detail: str = "Project not found",
        error_code: str = "PROJECT_NOT_FOUND",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class TaskNotFoundException(NotFoundException):
    """Exception for task not found"""

    def __init__(
        self,
        detail: str = "Task not found",
        error_code: str = "TASK_NOT_FOUND",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class ProjectMemberNotFoundException(NotFoundException):
    """Exception for project member not found"""

    def __init__(
        self,
        detail: str = "Project member not found",
        error_code: str = "PROJECT_MEMBER_NOT_FOUND",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class NotProjectMemberException(ForbiddenException):
    """Exception for user not being a project member"""

    def __init__(
        self,
        detail: str = "User is not a member of this project",
        error_code: str = "NOT_PROJECT_MEMBER",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class InsufficientProjectRoleException(ForbiddenException):
    """Exception for insufficient project role"""

    def __init__(
        self,
        detail: str = "Insufficient project role",
        error_code: str = "INSUFFICIENT_PROJECT_ROLE",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class ProjectLimitExceededException(BadRequestException):
    """Exception for exceeding project limit"""

    def __init__(
        self,
        detail: str = "Project limit exceeded",
        error_code: str = "PROJECT_LIMIT_EXCEEDED",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class TaskLimitExceededException(BadRequestException):
    """Exception for exceeding task limit"""

    def __init__(
        self,
        detail: str = "Task limit exceeded",
        error_code: str = "TASK_LIMIT_EXCEEDED",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class InvalidTaskStatusTransitionException(BadRequestException):
    """Exception for invalid task status transition"""

    def __init__(
        self,
        detail: str = "Invalid task status transition",
        error_code: str = "INVALID_TASK_STATUS_TRANSITION",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)
