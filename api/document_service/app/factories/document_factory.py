from typing import Any, Dict, List, Optional

from api.document_service.app.schemas.document import DocumentType
from api.shared.exceptions.document_exceptions import InvalidDocumentTypeException
from api.shared.models.document import Document


class DocumentFactory:
    """Factory for creating documents"""

    def create_document(
        self,
        document_type: DocumentType,
        name: str,
        project_id: str,
        creator_id: str,
        parent_id: Optional[str] = None,
        content_type: Optional[str] = None,
        url: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Create a document based on type.

        Args:
            document_type (DocumentType): Document type
            name (str): Document name
            project_id (str): Project ID
            creator_id (str): Creator ID
            parent_id (Optional[str], optional): Parent document ID. Defaults to None.
            content_type (Optional[str], optional): Content type. Defaults to None.
            url (Optional[str], optional): URL. Defaults to None.
            description (Optional[str], optional): Description. Defaults to None.
            tags (Optional[List[str]], optional): Tags. Defaults to None.
            meta_data (Optional[Dict[str, Any]], optional): Metadata. Defaults to None.

        Returns:
            Document: Created document

        Raises:
            InvalidDocumentTypeException: If document type is invalid
        """
        if document_type == DocumentType.FILE:
            return self._create_file_document(
                name=name,
                project_id=project_id,
                creator_id=creator_id,
                parent_id=parent_id,
                content_type=content_type,
                url=url,
                description=description,
                tags=tags,
                meta_data=meta_data,
            )
        elif document_type == DocumentType.FOLDER:
            return self._create_folder_document(
                name=name,
                project_id=project_id,
                creator_id=creator_id,
                parent_id=parent_id,
                description=description,
                tags=tags,
                meta_data=meta_data,
            )
        elif document_type == DocumentType.LINK:
            if url is None:
                raise InvalidDocumentTypeException("URL is required for link documents.")
            return self._create_link_document(
                name=name,
                project_id=project_id,
                creator_id=creator_id,
                parent_id=parent_id,
                url=url,
                description=description,
                tags=tags,
                meta_data=meta_data,
            )
        else:
            raise InvalidDocumentTypeException(
                f"Invalid document type: {document_type}"
            )

    def _create_file_document(
        self,
        name: str,
        project_id: str,
        creator_id: str,
        parent_id: Optional[str] = None,
        content_type: Optional[str] = None,
        url: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Create a file document.

        Args:
            name (str): Document name
            project_id (str): Project ID
            creator_id (str): Creator ID
            parent_id (Optional[str], optional): Parent document ID. Defaults to None.
            content_type (Optional[str], optional): Content type. Defaults to None.
            url (Optional[str], optional): URL. Defaults to None.
            description (Optional[str], optional): Description. Defaults to None.
            tags (Optional[List[str]], optional): Tags. Defaults to None.
            meta_data (Optional[Dict[str, Any]], optional): Metadata. Defaults to None.

        Returns:
            Document: Created document
        """
        return Document(
            name=name,
            project_id=project_id,
            parent_id=parent_id,
            type=DocumentType.FILE,
            content_type=content_type,
            url=url,
            description=description,
            version=1,
            creator_id=creator_id,
            tags=tags,
            meta_data=meta_data,
        )

    def _create_folder_document(
        self,
        name: str,
        project_id: str,
        creator_id: str,
        parent_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Create a folder document.

        Args:
            name (str): Document name
            project_id (str): Project ID
            creator_id (str): Creator ID
            parent_id (Optional[str], optional): Parent document ID. Defaults to None.
            description (Optional[str], optional): Description. Defaults to None.
            tags (Optional[List[str]], optional): Tags. Defaults to None.
            meta_data (Optional[Dict[str, Any]], optional): Metadata. Defaults to None.

        Returns:
            Document: Created document
        """
        return Document(
            name=name,
            project_id=project_id,
            parent_id=parent_id,
            type=DocumentType.FOLDER,
            description=description,
            version=1,
            creator_id=creator_id,
            tags=tags,
            meta_data=meta_data,
        )

    def _create_link_document(
        self,
        name: str,
        project_id: str,
        creator_id: str,
        url: str,
        parent_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Create a link document.

        Args:
            name (str): Document name
            project_id (str): Project ID
            creator_id (str): Creator ID
            url (str): URL
            parent_id (Optional[str], optional): Parent document ID. Defaults to None.
            description (Optional[str], optional): Description. Defaults to None.
            tags (Optional[List[str]], optional): Tags. Defaults to None.
            meta_data (Optional[Dict[str, Any]], optional): Metadata. Defaults to None.

        Returns:
            Document: Created document
        """
        return Document(
            name=name,
            project_id=project_id,
            parent_id=parent_id,
            type=DocumentType.LINK,
            url=url,
            description=description,
            version=1,
            creator_id=creator_id,
            tags=tags,
            meta_data=meta_data,
        )
