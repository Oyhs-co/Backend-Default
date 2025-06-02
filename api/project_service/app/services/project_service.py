from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from api.project_service.app.schemas.project import (
    ProjectCreateDTO,
    ProjectMemberCreateDTO,
    ProjectMemberResponseDTO,
    ProjectMemberUpdateDTO,
    ProjectResponseDTO,
    ProjectUpdateDTO,
    ProjectStatus,
)
from api.project_service.app.services.activity_service import ActivityService
from api.shared.exceptions.project_exceptions import (
    InsufficientProjectRoleException,
    NotProjectMemberException,
    ProjectNotFoundException,
)
from api.shared.models.project import Project, ProjectMember


class ProjectService:
    """Service for project operations"""

    def __init__(self, db: Session):
        """
        Initialize ProjectService.

        Args:
            db (Session): Database session
        """
        self.db = db
        self.activity_service = ActivityService(db)

    def create_project(
        self, project_data: ProjectCreateDTO, user_id: str
    ) -> ProjectResponseDTO:
        """
        Create a new project.

        Args:
            project_data (ProjectCreateDTO): Project data
            user_id (str): User ID

        Returns:
            ProjectResponseDTO: Created project
        """
        # Create project
        project = Project(
            name=project_data.name,
            description=project_data.description,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            status=project_data.status,
            owner_id=user_id,
            tags=(project_data.tags or {}),
            meta_data=(project_data.meta_data or {}),
        )

        # Add project to database
        self.db.add(project)
        self.db.flush()

        # Add owner as project member
        project_member = ProjectMember(
            project_id=project.id,
            user_id=user_id,
            role="owner",
            joined_at=datetime.now(timezone.utc),
        )

        # Add project member to database
        self.db.add(project_member)
        self.db.commit()
        self.db.refresh(project)

        # Log activity
        self.activity_service.log_activity(
            project_id=project.id,
            user_id=user_id,
            action="create",
            entity_type="project",
            entity_id=project.id,
            details={"name": project.name},
        )

        # Return project
        return self._project_to_dto(project)

    def get_project(self, project_id: str, user_id: str) -> ProjectResponseDTO:
        """
        Get a project.

        Args:
            project_id (str): Project ID
            user_id (str): User ID

        Returns:
            ProjectResponseDTO: Project

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Return project
        return self._project_to_dto(project)

    def update_project(
        self, project_id: str, project_data: ProjectUpdateDTO, user_id: str
    ) -> ProjectResponseDTO:
        """
        Update a project.

        Args:
            project_id (str): Project ID
            project_data (ProjectUpdateDTO): Project data
            user_id (str): User ID

        Returns:
            ProjectResponseDTO: Updated project

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
            InsufficientProjectRoleException: If user has insufficient role
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Check if user has sufficient role
        if project_member.role not in ["owner", "admin"]:
            raise InsufficientProjectRoleException()

        # Update project
        if project_data.name is not None:
            project.name = project_data.name

        if project_data.description is not None:
            project.description = project_data.description

        if project_data.start_date is not None:
            project.start_date = project_data.start_date

        if project_data.end_date is not None:
            project.end_date = project_data.end_date

        if project_data.status is not None:
            project.status = project_data.status.value

        if project_data.tags is not None:
            project.tags = project_data.tags

        if project_data.meta_data is not None:
            project.meta_data = project_data.meta_data

        # Update project in database
        project.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(project)

        # Log activity
        self.activity_service.log_activity(
            project_id=project.id,
            user_id=user_id,
            action="update",
            entity_type="project",
            entity_id=str(project.id),
            details=project_data.model_dump_json(exclude_none=True),
        )

        # Return project
        return self._project_to_dto(project)

    def delete_project(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a project.

        Args:
            project_id (str): Project ID
            user_id (str): User ID

        Returns:
            Dict[str, Any]: Delete response

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
            InsufficientProjectRoleException: If user has insufficient role
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Check if user has sufficient role
        if project_member.role != "owner":
            raise InsufficientProjectRoleException(
                "Only project owner can delete the project"
            )

        # Log activity before deletion
        self.activity_service.log_activity(
            project_id=project.id,
            user_id=user_id,
            action="delete",
            entity_type="project",
            entity_id=str(project.id),
            details=None,
        )

        # Delete project
        self.db.delete(project)
        self.db.commit()

        # Return success response
        return {"message": "Project deleted successfully"}

    def get_user_projects(self, user_id: str) -> List[ProjectResponseDTO]:
        """
        Get projects for a user.

        Args:
            user_id (str): User ID

        Returns:
            List[ProjectResponseDTO]: List of projects
        """
        # Get project members for user
        project_members = (
            self.db.query(ProjectMember).filter(ProjectMember.user_id == user_id).all()
        )

        # Get project IDs
        project_ids = [member.project_id for member in project_members]

        # Get projects
        projects = self.db.query(Project).filter(Project.id.in_(project_ids)).all()

        # Return projects
        return [self._project_to_dto(project) for project in projects]

    def add_project_member(
        self, project_id: str, member_data: ProjectMemberCreateDTO, user_id: str
    ) -> ProjectMemberResponseDTO:
        """
        Add a member to a project.

        Args:
            project_id (str): Project ID
            member_data (ProjectMemberCreateDTO): Member data
            user_id (str): User ID

        Returns:
            ProjectMemberResponseDTO: Added project member

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
            InsufficientProjectRoleException: If user has insufficient role
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Check if user has sufficient role
        if project_member.role not in ["owner", "admin"]:
            raise InsufficientProjectRoleException()

        # Check if member already exists
        existing_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == member_data.user_id,
            )
            .first()
        )

        if existing_member:
            # Update role if member already exists
            existing_member.role = member_data.role
            self.db.commit()
            self.db.refresh(existing_member)

            # Log activity
            self.activity_service.log_activity(
                project_id=project_id,
                user_id=user_id,
                action="update",
                entity_type="project_member",
                entity_id=str(existing_member.id),
                details={"user_id": member_data.user_id, "role": member_data.role},
            )

            # Return member
            return self._project_member_to_dto(existing_member)

        # Create project member
        new_member = ProjectMember(
            project_id=project_id,
            user_id=member_data.user_id,
            role=member_data.role,
            joined_at=datetime.now(timezone.utc),
        )

        # Add project member to database
        self.db.add(new_member)
        self.db.commit()
        self.db.refresh(new_member)

        # Log activity
        self.activity_service.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="add_member",
            entity_type="project_member",
            entity_id=str(new_member.id),
            details={"user_id": member_data.user_id, "role": member_data.role},
        )

        # Return member
        return self._project_member_to_dto(new_member)

    def update_project_member(
        self,
        project_id: str,
        member_id: str,
        member_data: ProjectMemberUpdateDTO,
        user_id: str,
    ) -> ProjectMemberResponseDTO:
        """
        Update a project member.

        Args:
            project_id (str): Project ID
            member_id (str): Member ID
            member_data (ProjectMemberUpdateDTO): Member data
            user_id (str): User ID

        Returns:
            ProjectMemberResponseDTO: Updated project member

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
            InsufficientProjectRoleException: If user has insufficient role
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Check if user has sufficient role
        if project_member.role not in ["owner", "admin"]:
            raise InsufficientProjectRoleException()

        # Get member to update
        member_to_update = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.id == member_id, ProjectMember.project_id == project_id
            )
            .first()
        )

        if not member_to_update:
            raise ProjectNotFoundException("Project member not found")

        # Check if trying to change owner role
        if member_to_update.role == "owner" and member_data.role != "owner":
            # Only owner can transfer ownership
            if project_member.role != "owner":
                raise InsufficientProjectRoleException(
                    "Only project owner can transfer ownership"
                )

        # Update member
        member_to_update.role = member_data.role
        self.db.commit()
        self.db.refresh(member_to_update)

        # Log activity
        self.activity_service.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="update_member",
            entity_type="project_member",
            entity_id=str(member_to_update.id),
            details={"role": member_data.role},
        )

        # Return member
        return self._project_member_to_dto(member_to_update)

    def remove_project_member(
        self, project_id: str, member_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Remove a project member.

        Args:
            project_id (str): Project ID
            member_id (str): Member ID
            user_id (str): User ID

        Returns:
            Dict[str, Any]: Remove response

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
            InsufficientProjectRoleException: If user has insufficient role
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Get member to remove
        member_to_remove = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.id == member_id, ProjectMember.project_id == project_id
            )
            .first()
        )

        if not member_to_remove:
            raise ProjectNotFoundException("Project member not found")

        # Check if trying to remove owner
        if member_to_remove.role == "owner":
            raise InsufficientProjectRoleException("Cannot remove project owner")

        # Check if user has sufficient role
        if (
            project_member.role not in ["owner", "admin"]
            and project_member.id != member_id
        ):
            raise InsufficientProjectRoleException()

        # Log activity before deletion
        self.activity_service.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="remove_member",
            entity_type="project_member",
            entity_id=str(project_member.id),
            details=None,
        )

        # Remove member
        self.db.delete(member_to_remove)
        self.db.commit()

        # Return success response
        return {"message": "Project member removed successfully"}

    def get_project_members(
        self, project_id: str, user_id: str
    ) -> List[ProjectMemberResponseDTO]:
        """
        Get project members.

        Args:
            project_id (str): Project ID
            user_id (str): User ID

        Returns:
            List[ProjectMemberResponseDTO]: List of project members

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Get project members
        project_members = (
            self.db.query(ProjectMember)
            .filter(ProjectMember.project_id == project_id)
            .all()
        )

        # Return project members
        return [self._project_member_to_dto(member) for member in project_members]

    def _project_to_dto(self, project: Project) -> ProjectResponseDTO:
        """
        Convert Project model to ProjectResponseDTO.

        Args:
            project (Project): Project model

        Returns:
            ProjectResponseDTO: Project DTO
        """
        return ProjectResponseDTO(
            id=project.id,
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            status=ProjectStatus(project.status),
            owner_id=project.owner_id,
            tags=project.tags if project.tags is not None else [],
            meta_data=project.meta_data if project.meta_data is not None else {},
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    def _project_member_to_dto(
        self, project_member: ProjectMember
    ) -> ProjectMemberResponseDTO:
        """
        Convert ProjectMember model to ProjectMemberResponseDTO.

        Args:
            project_member (ProjectMember): ProjectMember model

        Returns:
            ProjectMemberResponseDTO: ProjectMember DTO
        """
        return ProjectMemberResponseDTO(
            id=project_member.id,
            project_id=project_member.project_id,
            user_id=project_member.user_id,
            role=project_member.role,
            joined_at=project_member.joined_at,
        )
