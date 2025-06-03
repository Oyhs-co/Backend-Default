from typing import Any, List, Optional

from dotenv import load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    Form,
    Path,
    Query,
    Security,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.document_service.app.schemas.document import (
    DocumentCreateDTO,
    DocumentPermissionCreateDTO,
    DocumentPermissionDTO,
    DocumentPermissionUpdateDTO,
    DocumentResponseDTO,
    DocumentUpdateDTO,
    DocumentUploadResponseDTO,
    DocumentVersionDTO,
)
from api.document_service.app.services.document_service import DocumentService
from api.shared.exceptions.auth_exceptions import InvalidTokenException
from api.shared.utils.db import get_db
from api.shared.utils.jwt import decode_token
from api.shared.middleware.auth_middleware import auth_middleware

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TaskHub Document Service",
    description="Document management service for TaskHub platform",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Security(oauth2_scheme)) -> str:
    """
    Get current user ID from token.

    Args:
        token (str): JWT token

    Returns:
        str: User ID

    Raises:
        InvalidTokenException: If token is invalid
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidTokenException()

        return user_id
    except Exception:
        raise InvalidTokenException()


# Document endpoints
@app.post("/documents", response_model=DocumentResponseDTO, tags=["Documents"])
async def create_document(
    document_data: DocumentCreateDTO,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Create a new document.

    Args:
        document_data (DocumentCreateDTO): Document data
        db (Session): Database session
        user_id (str): User ID

    Returns:
        DocumentResponseDTO: Created document
    """
    document_service = DocumentService(db)
    return document_service.create_document(document_data, user_id)


@app.get(
    "/documents/{document_id}", response_model=DocumentResponseDTO, tags=["Documents"]
)
async def get_document(
    document_id: str = Path(..., description="Document ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get a document.

    Args:
        document_id (str): Document ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        DocumentResponseDTO: Document
    """
    document_service = DocumentService(db)
    return document_service.get_document(document_id, user_id)


@app.put(
    "/documents/{document_id}", response_model=DocumentResponseDTO, tags=["Documents"]
)
async def update_document(
    document_data: DocumentUpdateDTO,
    document_id: str = Path(..., description="Document ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Update a document.

    Args:
        document_data (DocumentUpdateDTO): Document data
        document_id (str): Document ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        DocumentResponseDTO: Updated document
    """
    document_service = DocumentService(db)
    return document_service.update_document(document_id, document_data, user_id)


@app.delete("/documents/{document_id}", tags=["Documents"])
async def delete_document(
    document_id: str = Path(..., description="Document ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Delete a document.

    Args:
        document_id (str): Document ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        Dict[str, Any]: Delete response
    """
    document_service = DocumentService(db)
    return document_service.delete_document(document_id, user_id)


@app.get(
    "/projects/{project_id}/documents",
    response_model=List[DocumentResponseDTO],
    tags=["Documents"],
)
async def get_project_documents(
    project_id: str = Path(..., description="Project ID"),
    parent_id: Optional[str] = Query(None, description="Parent document ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get documents for a project.

    Args:
        project_id (str): Project ID
        parent_id (Optional[str], optional): Parent document ID. Defaults to None.
        db (Session): Database session
        user_id (str): User ID

    Returns:
        List[DocumentResponseDTO]: List of documents
    """
    document_service = DocumentService(db)
    return document_service.get_project_documents(project_id, user_id, parent_id)


@app.post(
    "/documents/upload", response_model=DocumentUploadResponseDTO, tags=["Documents"]
)
async def upload_document(
    document_data: DocumentCreateDTO,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Upload a document.

    Args:
        document_data (DocumentCreateDTO): Document data
        db (Session): Database session
        user_id (str): User ID

    Returns:
        DocumentUploadResponseDTO: Upload response
    """
    document_service = DocumentService(db)
    return document_service.upload_document(document_data, user_id)


# Document version endpoints
@app.post(
    "/documents/{document_id}/versions",
    response_model=DocumentVersionDTO,
    tags=["Document Versions"],
)
async def create_document_version(
    content_type: str = Form(..., description="Content type"),
    changes: str = Form(..., description="Changes description"),
    document_id: str = Path(..., description="Document ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Create a new document version.

    Args:
        content_type (str): Content type
        changes (str): Changes description
        document_id (str): Document ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        DocumentVersionDTO: Created document version
    """
    document_service = DocumentService(db)
    return document_service.create_document_version(
        document_id, content_type, changes, user_id
    )


@app.get(
    "/documents/{document_id}/versions",
    response_model=List[DocumentVersionDTO],
    tags=["Document Versions"],
)
async def get_document_versions(
    document_id: str = Path(..., description="Document ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get versions for a document.

    Args:
        document_id (str): Document ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        List[DocumentVersionDTO]: List of document versions
    """
    document_service = DocumentService(db)
    return document_service.get_document_versions(document_id, user_id)


@app.get(
    "/documents/{document_id}/versions/{version}",
    response_model=DocumentVersionDTO,
    tags=["Document Versions"],
)
async def get_document_version(
    document_id: str = Path(..., description="Document ID"),
    version: int = Path(..., description="Version number"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get a specific document version.

    Args:
        document_id (str): Document ID
        version (int): Version number
        db (Session): Database session
        user_id (str): User ID

    Returns:
        DocumentVersionDTO: Document version
    """
    document_service = DocumentService(db)
    return document_service.get_document_version(document_id, version, user_id)


# Document permission endpoints
@app.post(
    "/documents/{document_id}/permissions",
    response_model=DocumentPermissionDTO,
    tags=["Document Permissions"],
)
async def add_document_permission(
    permission_data: DocumentPermissionCreateDTO,
    document_id: str = Path(..., description="Document ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Add a permission to a document.

    Args:
        permission_data (DocumentPermissionCreateDTO): Permission data
        document_id (str): Document ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        DocumentPermissionDTO: Added document permission
    """
    document_service = DocumentService(db)
    return document_service.add_document_permission(
        document_id, permission_data, user_id
    )


@app.put(
    "/documents/{document_id}/permissions/{permission_id}",
    response_model=DocumentPermissionDTO,
    tags=["Document Permissions"],
)
async def update_document_permission(
    permission_data: DocumentPermissionUpdateDTO,
    document_id: str = Path(..., description="Document ID"),
    permission_id: str = Path(..., description="Permission ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Update a document permission.

    Args:
        permission_data (DocumentPermissionUpdateDTO): Permission data
        document_id (str): Document ID
        permission_id (str): Permission ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        DocumentPermissionDTO: Updated document permission
    """
    document_service = DocumentService(db)
    return document_service.update_document_permission(
        document_id, permission_id, permission_data, user_id
    )


@app.delete(
    "/documents/{document_id}/permissions/{permission_id}",
    tags=["Document Permissions"],
)
async def delete_document_permission(
    document_id: str = Path(..., description="Document ID"),
    permission_id: str = Path(..., description="Permission ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Delete a document permission.

    Args:
        document_id (str): Document ID
        permission_id (str): Permission ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        Dict[str, Any]: Delete response
    """
    document_service = DocumentService(db)
    return document_service.delete_document_permission(
        document_id, permission_id, user_id
    )


@app.get(
    "/documents/{document_id}/permissions",
    response_model=List[DocumentPermissionDTO],
    tags=["Document Permissions"],
)
async def get_document_permissions(
    document_id: str = Path(..., description="Document ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get permissions for a document.

    Args:
        document_id (str): Document ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        List[DocumentPermissionDTO]: List of document permissions
    """
    document_service = DocumentService(db)
    return document_service.get_document_permissions(document_id, user_id)


@app.get("/health", tags=["Health"])
async def health_check() -> Any:
    """
    Health check endpoint.

    Returns:
        Dict[str, str]: Health status
    """
    return {"status": "healthy"}
