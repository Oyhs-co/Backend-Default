from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from api.project_service.app.schemas.activity import ActivityLogResponseDTO
from api.shared.exceptions.project_exceptions import ProjectNotFoundException
from api.shared.models.project import ActivityLog


class ActivityService:
    """Service for activity log operations"""

    def __init__(self, db: Session):
        """
        Initialize ActivityService.

        Args:
            db (Session): Database session
        """
        self.db = db

    def log_activity(
        self,
        project_id: str,
        user_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> ActivityLogResponseDTO:
        """
        Log an activity.

        Args:
            project_id (str): Project ID
            user_id (str): User ID
            action (str): Action performed
            entity_type (str): Entity type
            entity_id (str): Entity ID
            details (Dict[str, Any], optional): Activity details

        Returns:
            ActivityLogResponseDTO: Logged activity
        """
        # Create activity log
        activity_log = ActivityLog(
            project_id=project_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )

        # Add activity log to database
        self.db.add(activity_log)
        self.db.commit()
        self.db.refresh(activity_log)

        # Return activity log
        return self._activity_log_to_dto(activity_log)

    def get_project_activities(
        self, project_id: str, limit: int = 100, offset: int = 0
    ) -> List[ActivityLogResponseDTO]:
        """
        Get activities for a project.

        Args:
            project_id (str): Project ID
            limit (int, optional): Limit. Defaults to 100.
            offset (int, optional): Offset. Defaults to 0.

        Returns:
            List[ActivityLogResponseDTO]: List of activities

        Raises:
            ProjectNotFoundException: If project not found
        """
        # Get activities
        activities = (
            self.db.query(ActivityLog)
            .filter(ActivityLog.project_id == project_id)
            .order_by(ActivityLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Return activities
        return [self._activity_log_to_dto(activity) for activity in activities]

    def get_entity_activities(
        self, entity_type: str, entity_id: str, limit: int = 100, offset: int = 0
    ) -> List[ActivityLogResponseDTO]:
        """
        Get activities for an entity.

        Args:
            entity_type (str): Entity type
            entity_id (str): Entity ID
            limit (int, optional): Limit. Defaults to 100.
            offset (int, optional): Offset. Defaults to 0.

        Returns:
            List[ActivityLogResponseDTO]: List of activities
        """
        # Get activities
        activities = (
            self.db.query(ActivityLog)
            .filter(
                ActivityLog.entity_type == entity_type,
                ActivityLog.entity_id == entity_id,
            )
            .order_by(ActivityLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Return activities
        return [self._activity_log_to_dto(activity) for activity in activities]

    def get_user_activities(
        self, user_id: str, limit: int = 100, offset: int = 0
    ) -> List[ActivityLogResponseDTO]:
        """
        Get activities for a user.

        Args:
            user_id (str): User ID
            limit (int, optional): Limit. Defaults to 100.
            offset (int, optional): Offset. Defaults to 0.

        Returns:
            List[ActivityLogResponseDTO]: List of activities
        """
        # Get activities
        activities = (
            self.db.query(ActivityLog)
            .filter(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Return activities
        return [self._activity_log_to_dto(activity) for activity in activities]

    def _activity_log_to_dto(self, activity_log: ActivityLog) -> ActivityLogResponseDTO:
        """
        Convert ActivityLog model to ActivityLogResponseDTO.

        Args:
            activity_log (ActivityLog): ActivityLog model

        Returns:
            ActivityLogResponseDTO: ActivityLog DTO
        """
        return ActivityLogResponseDTO(
            id=activity_log.id,
            project_id=activity_log.project_id,
            user_id=activity_log.user_id,
            action=activity_log.action,
            entity_type=activity_log.entity_type,
            entity_id=activity_log.entity_id,
            details=(activity_log.details or {}),
            created_at=activity_log.created_at,
        )
