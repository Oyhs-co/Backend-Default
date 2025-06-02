from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from api.document_service.app.factories.document_factory import DocumentFactory
from api.document_service.app.schemas.document import (
    DocumentCreateDTO,
    DocumentPermissionCreateDTO,
    DocumentPermissionDTO,
    DocumentPermissionUpdateDTO,
    DocumentResponseDTO,
    DocumentType,
    DocumentUpdateDTO,
    DocumentUploadResponseDTO,
    DocumentVersionDTO,
)
from api.shared.exceptions.document_exceptions import (
    DocumentNotFoundException,
    DocumentPermissionNotFoundException,
    DocumentStorageException,
    DocumentVersionNotFoundException,
    InsufficientDocumentPermissionException,
    InvalidDocumentTypeException,
)
from api.shared.exceptions.project_exceptions import (
    NotProjectMemberException,
    ProjectNotFoundException,
)
from api.shared.models.document import Document, DocumentPermission, DocumentVersion
from api.shared.models.project import Project, ProjectMember
from api.shared.utils.supabase import SupabaseManager


class DocumentService:
    """Service for document operations"""

    def __init__(self, db: Session):
        """
        Initialize DocumentService.

        Args:
            db (Session): Database session
        """
        self.db = db
        self.supabase_manager = SupabaseManager()
        self.document_factory = DocumentFactory()

    def create_document(
        self, document_data: DocumentCreateDTO, user_id: str
    ) -> DocumentResponseDTO:
        """
        Create a new document.

        Args:
            document_data (DocumentCreateDTO): Document data
            user_id (str): User ID

        Returns:
            DocumentResponseDTO: Created document

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
            InvalidDocumentTypeException: If document type is invalid
        """
        # Get project
        project = (
            self.db.query(Project)
            .filter(Project.id == document_data.project_id)
            .first()
        )

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == document_data.project_id,
                ProjectMember.user_id == user_id,
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Check if parent document exists
        if document_data.parent_id:
            parent_document = (
                self.db.query(Document)
                .filter(
                    Document.id == document_data.parent_id,
                    Document.project_id == document_data.project_id,
                )
                .first()
            )

            if not parent_document:
                raise DocumentNotFoundException("Parent document not found")

            # Check if parent document is a folder
            if parent_document.type != DocumentType.FOLDER:
                raise InvalidDocumentTypeException("Parent document must be a folder")

        # Create document using factory
        document = self.document_factory.create_document(
            document_type=document_data.type,
            name=document_data.name,
            project_id=document_data.project_id,
            parent_id=document_data.parent_id,
            content_type=document_data.content_type,
            url=document_data.url,
            description=document_data.description,
            creator_id=user_id,
            tags=document_data.tags if document_data.tags is not None else [],
            meta_data=(
                document_data.meta_data if document_data.meta_data is not None else {}
            ),
        )

        # Add document to database
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        # Create document version for files
        if document.type == DocumentType.FILE:
            document_version = DocumentVersion(
                document_id=document.id,
                version=1,
                content_type=document.content_type,
                url=document.url,
                creator_id=user_id,
                changes="Initial version",
            )

            # Add document version to database
            self.db.add(document_version)
            self.db.commit()

        # Create default permission for creator
        document_permission = DocumentPermission(
            document_id=document.id,
            user_id=user_id,
            can_view=True,
            can_edit=True,
            can_delete=True,
            can_share=True,
        )

        # Add document permission to database
        self.db.add(document_permission)
        self.db.commit()

        # Return document
        return self._document_to_dto(document)

    def get_document(self, document_id: str, user_id: str) -> DocumentResponseDTO:
        """
        Get a document.

        Args:
            document_id (str): Document ID
            user_id (str): User ID

        Returns:
            DocumentResponseDTO: Document

        Raises:
            DocumentNotFoundException: If document not found
            InsufficientDocumentPermissionException: If user has insufficient permission
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            raise DocumentNotFoundException()

        # Check if user has permission to view document
        if not self._has_permission(document_id, user_id, "view"):
            raise InsufficientDocumentPermissionException(
                "User does not have permission to view this document"
            )

        # Return document
        return self._document_to_dto(document)

    def update_document(
        self, document_id: str, document_data: DocumentUpdateDTO, user_id: str
    ) -> DocumentResponseDTO:
        """
        Update a document.

        Args:
            document_id (str): Document ID
            document_data (DocumentUpdateDTO): Document data
            user_id (str): User ID

        Returns:
            DocumentResponseDTO: Updated document

        Raises:
            DocumentNotFoundException: If document not found
            InsufficientDocumentPermissionException: If user has insufficient permission
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            raise DocumentNotFoundException()

        # Check if user has permission to edit document
        if not self._has_permission(document_id, user_id, "edit"):
            raise InsufficientDocumentPermissionException(
                "User does not have permission to edit this document"
            )

        # Check if parent document exists
        if document_data.parent_id:
            parent_document = (
                self.db.query(Document)
                .filter(
                    Document.id == document_data.parent_id,
                    Document.project_id == document.project_id,
                )
                .first()
            )

            if not parent_document:
                raise DocumentNotFoundException("Parent document not found")

            # Check if parent document is a folder
            if parent_document.type != DocumentType.FOLDER:
                raise InvalidDocumentTypeException("Parent document must be a folder")

        # Update document
        if document_data.name is not None:
            document.name = document_data.name

        if document_data.parent_id is not None:
            document.parent_id = document_data.parent_id

        if document_data.description is not None:
            document.description = document_data.description

        if document_data.tags is not None:
            document.tags = document_data.tags

        if document_data.meta_data is not None:
            document.meta_data = document_data.meta_data

        # Update document in database
        document.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(document)

        # Return document
        return self._document_to_dto(document)

    def delete_document(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a document.

        Args:
            document_id (str): Document ID
            user_id (str): User ID

        Returns:
            Dict[str, Any]: Delete response

        Raises:
            DocumentNotFoundException: If document not found
            InsufficientDocumentPermissionException: If user has insufficient permission
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            raise DocumentNotFoundException()

        # Check if user has permission to delete document
        if not self._has_permission(document_id, user_id, "delete"):
            raise InsufficientDocumentPermissionException(
                "User does not have permission to delete this document"
            )

        # Delete document from storage if it's a file
        if document.type == DocumentType.FILE and document.url:
            try:
                # Extract bucket name and file path from URL
                # This is a simplified example, actual implementation may vary
                url_parts = document.url.split("/")
                bucket_name = url_parts[-2]
                file_path = url_parts[-1]

                # Delete file from storage
                self.supabase_manager.delete_file(bucket_name, file_path)
            except Exception as e:
                # Log error but continue with document deletion
                print(f"Error deleting file from storage: {e}")

        # Delete document
        self.db.delete(document)
        self.db.commit()

        # Return success response
        return {"message": "Document deleted successfully"}

    def get_project_documents(
        self, project_id: str, user_id: str, parent_id: Optional[str] = None
    ) -> List[DocumentResponseDTO]:
        """
        Get documents for a project.

        Args:
            project_id (str): Project ID
            user_id (str): User ID
            parent_id (Optional[str], optional): Parent document ID. Defaults to None.

        Returns:
            List[DocumentResponseDTO]: List of documents

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

        # Get documents
        query = self.db.query(Document).filter(Document.project_id == project_id)

        if parent_id is not None:
            query = query.filter(Document.parent_id == parent_id)
        else:
            query = query.filter(Document.parent_id.is_(None))

        documents = query.all()

        # Filter documents based on user permissions
        allowed_documents = []
        for document in documents:
            if self._has_permission(document.id, user_id, "view"):
                allowed_documents.append(document)

        # Return documents
        return [self._document_to_dto(document) for document in allowed_documents]

    def upload_document(
        self, document_data: DocumentCreateDTO, user_id: str
    ) -> DocumentUploadResponseDTO:
        """
        Upload a document.

        Args:
            document_data (DocumentCreateDTO): Document data
            user_id (str): User ID

        Returns:
            DocumentUploadResponseDTO: Upload response

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
            InvalidDocumentTypeException: If document type is invalid
        """
        # Check if document type is file
        if document_data.type != DocumentType.FILE:
            raise InvalidDocumentTypeException("Document type must be file for upload")

        # Create document
        document = self.create_document(document_data, user_id)

        # Generate upload URL
        bucket_name = f"project-{document_data.project_id}"
        file_path = f"{document.id}/{document.name}"

        try:
            # Create bucket if it doesn't exist
            try:
                self.supabase_manager.create_bucket(bucket_name)
            except Exception:
                # Bucket may already exist
                pass

            # Generate upload URL
            upload_url = self.supabase_manager.get_file_url(bucket_name, file_path)

            # Return upload response
            return DocumentUploadResponseDTO(document=document, upload_url=upload_url)
        except Exception as e:
            # Delete document if upload URL generation fails
            self.db.delete(
                self.db.query(Document).filter(Document.id == document.id).first()
            )
            self.db.commit()

            raise DocumentStorageException(f"Failed to generate upload URL: {e}")

    def create_document_version(
        self, document_id: str, content_type: str, changes: str, user_id: str
    ) -> DocumentVersionDTO:
        """
        Create a new document version.

        Args:
            document_id (str): Document ID
            content_type (str): Content type
            changes (str): Changes description
            user_id (str): User ID

        Returns:
            DocumentVersionDTO: Created document version

        Raises:
            DocumentNotFoundException: If document not found
            InsufficientDocumentPermissionException: If user has insufficient permission
            InvalidDocumentTypeException: If document type is invalid
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            raise DocumentNotFoundException()

        # Check if document type is file
        if document.type != DocumentType.FILE:
            raise InvalidDocumentTypeException(
                "Document type must be file for versioning"
            )

        # Check if user has permission to edit document
        if not self._has_permission(document_id, user_id, "edit"):
            raise InsufficientDocumentPermissionException(
                "User does not have permission to edit this document"
            )

        # Get latest version
        latest_version = (
            self.db.query(DocumentVersion)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version.desc())
            .first()
        )

        # Calculate new version number
        new_version = 1 if not latest_version else latest_version.version + 1

        # Generate file URL
        bucket_name = f"project-{document.project_id}"
        file_path = f"{document.id}/v{new_version}/{document.name}"
        url = self.supabase_manager.get_file_url(bucket_name, file_path)

        # Create document version
        document_version = DocumentVersion(
            document_id=document_id,
            version=new_version,
            content_type=content_type,
            url=url,
            creator_id=user_id,
            changes=changes,
        )

        # Add document version to database
        self.db.add(document_version)

        # Update document
        document.version = new_version
        document.content_type = content_type
        document.url = url
        document.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(document_version)

        # Return document version
        return self._document_version_to_dto(document_version)

    def get_document_versions(
        self, document_id: str, user_id: str
    ) -> List[DocumentVersionDTO]:
        """
        Get versions for a document.

        Args:
            document_id (str): Document ID
            user_id (str): User ID

        Returns:
            List[DocumentVersionDTO]: List of document versions

        Raises:
            DocumentNotFoundException: If document not found
            InsufficientDocumentPermissionException: If user has insufficient permission
            InvalidDocumentTypeException: If document type is invalid
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            raise DocumentNotFoundException()

        # Check if document type is file
        if document.type != DocumentType.FILE:
            raise InvalidDocumentTypeException(
                "Document type must be file for versioning"
            )

        # Check if user has permission to view document
        if not self._has_permission(document_id, user_id, "view"):
            raise InsufficientDocumentPermissionException(
                "User does not have permission to view this document"
            )

        # Get document versions
        document_versions = (
            self.db.query(DocumentVersion)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version.desc())
            .all()
        )

        # Return document versions
        return [self._document_version_to_dto(version) for version in document_versions]

    def get_document_version(
        self, document_id: str, version: int, user_id: str
    ) -> DocumentVersionDTO:
        """
        Get a specific document version.

        Args:
            document_id (str): Document ID
            version (int): Version number
            user_id (str): User ID

        Returns:
            DocumentVersionDTO: Document version

        Raises:
            DocumentNotFoundException: If document not found
            DocumentVersionNotFoundException: If document version not found
            InsufficientDocumentPermissionException: If user has insufficient permission
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            raise DocumentNotFoundException()

        # Check if user has permission to view document
        if not self._has_permission(document_id, user_id, "view"):
            raise InsufficientDocumentPermissionException(
                "User does not have permission to view this document"
            )

        # Get document version
        document_version = (
            self.db.query(DocumentVersion)
            .filter(
                DocumentVersion.document_id == document_id,
                DocumentVersion.version == version,
            )
            .first()
        )

        # Check if document version exists
        if not document_version:
            raise DocumentVersionNotFoundException()

        # Return document version
        return self._document_version_to_dto(document_version)

    def add_document_permission(
        self,
        document_id: str,
        permission_data: DocumentPermissionCreateDTO,
        user_id: str,
    ) -> DocumentPermissionDTO:
        """
        Add a permission to a document.

        Args:
            document_id (str): Document ID
            permission_data (DocumentPermissionCreateDTO): Permission data
            user_id (str): User ID

        Returns:
            DocumentPermissionDTO: Added document permission

        Raises:
            DocumentNotFoundException: If document not found
            InsufficientDocumentPermissionException: If user has insufficient permission
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            raise DocumentNotFoundException()

        # Check if user has permission to share document
        if not self._has_permission(document_id, user_id, "share"):
            raise InsufficientDocumentPermissionException(
                "User does not have permission to share this document"
            )

        # Check if permission already exists
        existing_permission = None
        if permission_data.user_id:
            existing_permission = (
                self.db.query(DocumentPermission)
                .filter(
                    DocumentPermission.document_id == document_id,
                    DocumentPermission.user_id == permission_data.user_id,
                )
                .first()
            )
        elif permission_data.role_id:
            existing_permission = (
                self.db.query(DocumentPermission)
                .filter(
                    DocumentPermission.document_id == document_id,
                    DocumentPermission.role_id == permission_data.role_id,
                )
                .first()
            )

        if existing_permission:
            # Update existing permission
            existing_permission.can_view = permission_data.can_view
            existing_permission.can_edit = permission_data.can_edit
            existing_permission.can_delete = permission_data.can_delete
            existing_permission.can_share = permission_data.can_share
            existing_permission.updated_at = datetime.now(timezone.utc)

            self.db.commit()
            self.db.refresh(existing_permission)

            return self._document_permission_to_dto(existing_permission)

        # Create document permission
        document_permission = DocumentPermission(
            document_id=document_id,
            user_id=permission_data.user_id,
            role_id=permission_data.role_id,
            can_view=permission_data.can_view,
            can_edit=permission_data.can_edit,
            can_delete=permission_data.can_delete,
            can_share=permission_data.can_share,
        )

        # Add document permission to database
        self.db.add(document_permission)
        self.db.commit()
        self.db.refresh(document_permission)

        # Return document permission
        return self._document_permission_to_dto(document_permission)

    def update_document_permission(
        self,
        document_id: str,
        permission_id: str,
        permission_data: DocumentPermissionUpdateDTO,
        user_id: str,
    ) -> DocumentPermissionDTO:
        """
        Update a document permission.

        Args:
            document_id (str): Document ID
            permission_id (str): Permission ID
            permission_data (DocumentPermissionUpdateDTO): Permission data
            user_id (str): User ID

        Returns:
            DocumentPermissionDTO: Updated document permission

        Raises:
            DocumentNotFoundException: If document not found
            DocumentPermissionNotFoundException: If document permission not found
            InsufficientDocumentPermissionException: If user has insufficient permission
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            raise DocumentNotFoundException()

        # Check if user has permission to share document
        if not self._has_permission(document_id, user_id, "share"):
            raise InsufficientDocumentPermissionException(
                "User does not have permission to share this document"
            )

        # Get document permission
        document_permission = (
            self.db.query(DocumentPermission)
            .filter(
                DocumentPermission.id == permission_id,
                DocumentPermission.document_id == document_id,
            )
            .first()
        )

        # Check if document permission exists
        if not document_permission:
            raise DocumentPermissionNotFoundException()

        # Update document permission
        if permission_data.can_view is not None:
            document_permission.can_view = permission_data.can_view

        if permission_data.can_edit is not None:
            document_permission.can_edit = permission_data.can_edit

        if permission_data.can_delete is not None:
            document_permission.can_delete = permission_data.can_delete

        if permission_data.can_share is not None:
            document_permission.can_share = permission_data.can_share

        # Update document permission in database
        document_permission.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(document_permission)

        # Return document permission
        return self._document_permission_to_dto(document_permission)

    def delete_document_permission(
        self, document_id: str, permission_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Delete a document permission.

        Args:
            document_id (str): Document ID
            permission_id (str): Permission ID
            user_id (str): User ID

        Returns:
            Dict[str, Any]: Delete response

        Raises:
            DocumentNotFoundException: If document not found
            DocumentPermissionNotFoundException: If document permission not found
            InsufficientDocumentPermissionException: If user has insufficient permission
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            raise DocumentNotFoundException()

        # Check if user has permission to share document
        if not self._has_permission(document_id, user_id, "share"):
            raise InsufficientDocumentPermissionException(
                "User does not have permission to share this document"
            )

        # Get document permission
        document_permission = (
            self.db.query(DocumentPermission)
            .filter(
                DocumentPermission.id == permission_id,
                DocumentPermission.document_id == document_id,
            )
            .first()
        )

        # Check if document permission exists
        if not document_permission:
            raise DocumentPermissionNotFoundException()

        # Check if trying to delete owner's permission
        if document_permission.user_id == document.creator_id:
            raise InsufficientDocumentPermissionException(
                "Cannot delete owner's permission"
            )

        # Delete document permission
        self.db.delete(document_permission)
        self.db.commit()

        # Return success response
        return {"message": "Document permission deleted successfully"}

    def get_document_permissions(
        self, document_id: str, user_id: str
    ) -> List[DocumentPermissionDTO]:
        """
        Get permissions for a document.

        Args:
            document_id (str): Document ID
            user_id (str): User ID

        Returns:
            List[DocumentPermissionDTO]: List of document permissions

        Raises:
            DocumentNotFoundException: If document not found
            InsufficientDocumentPermissionException: If user has insufficient permission
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            raise DocumentNotFoundException()

        # Check if user has permission to view document
        if not self._has_permission(document_id, user_id, "view"):
            raise InsufficientDocumentPermissionException(
                "User does not have permission to view this document"
            )

        # Get document permissions
        document_permissions = (
            self.db.query(DocumentPermission)
            .filter(DocumentPermission.document_id == document_id)
            .all()
        )

        # Return document permissions
        return [
            self._document_permission_to_dto(permission)
            for permission in document_permissions
        ]

    def _has_permission(
        self, document_id: str, user_id: str, permission_type: str
    ) -> bool:
        """
        Check if user has permission for a document.

        Args:
            document_id (str): Document ID
            user_id (str): User ID
            permission_type (str): Permission type ('view', 'edit', 'delete', 'share')

        Returns:
            bool: True if user has permission, False otherwise
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()

        # Check if document exists
        if not document:
            return False

        # Check if user is document creator
        if document.creator_id == user_id:
            return True

        # Get user's direct permission
        user_permission = (
            self.db.query(DocumentPermission)
            .filter(
                DocumentPermission.document_id == document_id,
                DocumentPermission.user_id == user_id,
            )
            .first()
        )

        if user_permission:
            if permission_type == "view" and user_permission.can_view:
                return True
            elif permission_type == "edit" and user_permission.can_edit:
                return True
            elif permission_type == "delete" and user_permission.can_delete:
                return True
            elif permission_type == "share" and user_permission.can_share:
                return True

        # Get user's roles
        project_member_roles = (
            self.db.query(ProjectMember.role)
            .filter(
                ProjectMember.project_id == document.project_id,
                ProjectMember.user_id == user_id,
            )
            .first()
        )

        # Check project role (owner/admin implies all permissions for this simplified check)
        if project_member_roles and project_member_roles[0] in ["owner", "admin"]:
            return True

        # If no direct user permission, check for role-based permissions
        # This part needs a clear definition of how `Role` and `DocumentPermission` are linked.
        # Assuming `DocumentPermission.role_id` links to a generic `Role` model which is then linked to user via `user_roles` table.
        # This part is complex and depends on the exact `Role` model structure and its relation to `User`.
        # For now, let's assume a simplified check or comment it out if it's too undefined.

        # Placeholder for a more complex role permission check if needed.
        # user_app_roles = self.db.query(UserRole).filter(UserRole.user_id == user_id).all() # Hypothetical UserRole model
        # role_ids = [app_role.role_id for app_role in user_app_roles]
        # for role_id in role_ids:
        #     role_permission = (
        #         self.db.query(DocumentPermission)
        #         .filter(
        #             DocumentPermission.document_id == document_id,
        #             DocumentPermission.role_id == role_id, # This role_id should match the one in DocumentPermission
        #         )
        #         .first()
        #     )
        #     if role_permission:
        #         if permission_type == "view" and role_permission.can_view:
        #             return True
        #         elif permission_type == "edit" and role_permission.can_edit:
        #             return True
        #         elif permission_type == "delete" and role_permission.can_delete:
        #             return True
        #         elif permission_type == "share" and role_permission.can_share:
        #             return True

        return False

    def _document_to_dto(self, document: Document) -> DocumentResponseDTO:
        """
        Convert Document model to DocumentResponseDTO.

        Args:
            document (Document): Document model

        Returns:
            DocumentResponseDTO: Document DTO
        """
        return DocumentResponseDTO(
            id=document.id,
            name=document.name,
            project_id=document.project_id,
            parent_id=document.parent_id,
            type=document.type,
            content_type=document.content_type,
            size=document.size,
            url=document.url,
            description=document.description,
            version=document.version,
            creator_id=document.creator_id,
            tags=document.tags if document.tags is not None else [],
            meta_data=document.meta_data if document.meta_data is not None else {},
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

    def _document_version_to_dto(
        self, document_version: DocumentVersion
    ) -> DocumentVersionDTO:
        """
        Convert DocumentVersion model to DocumentVersionDTO.

        Args:
            document_version (DocumentVersion): DocumentVersion model

        Returns:
            DocumentVersionDTO: DocumentVersion DTO
        """
        return DocumentVersionDTO(
            id=document_version.id,
            document_id=document_version.document_id,
            version=document_version.version,
            size=document_version.size,
            content_type=document_version.content_type,
            url=document_version.url,
            creator_id=document_version.creator_id,
            changes=document_version.changes,
            created_at=document_version.created_at,
        )

    def _document_permission_to_dto(
        self, document_permission: DocumentPermission
    ) -> DocumentPermissionDTO:
        """
        Convert DocumentPermission model to DocumentPermissionDTO.

        Args:
            document_permission (DocumentPermission): DocumentPermission model

        Returns:
            DocumentPermissionDTO: DocumentPermission DTO
        """
        return DocumentPermissionDTO(
            id=document_permission.id,
            document_id=document_permission.document_id,
            user_id=document_permission.user_id,
            role_id=document_permission.role_id,
            can_view=document_permission.can_view,
            can_edit=document_permission.can_edit,
            can_delete=document_permission.can_delete,
            can_share=document_permission.can_share,
            created_at=document_permission.created_at,
            updated_at=document_permission.updated_at,
        )
