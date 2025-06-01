from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from api.shared.models.external_tools import OAuthProvider, ExternalToolConnection, ExternalResource
from api.external-tools-service.app.schemas.external_tools import (
    OAuthProviderDTO,
    OAuthRequestDTO,
    OAuthCallbackDTO,
    ExternalToolConnectionDTO,
    ExternalToolConnectionCreateDTO,
    ExternalResourceDTO,
    ExternalResourceSyncDTO,
    ExternalToolType
)
from api.external-tools-service.app.adapters.oauth_adapter import OAuthAdapterFactory


class ExternalToolsService:
    """Service for external tools operations"""
    
    def __init__(self, db: Session):
        """
        Initialize ExternalToolsService.
        
        Args:
            db (Session): Database session
        """
        self.db = db
        self.adapter_factory = OAuthAdapterFactory()
    
    def get_oauth_providers(self) -> List[OAuthProviderDTO]:
        """
        Get OAuth providers.
        
        Returns:
            List[OAuthProviderDTO]: List of OAuth providers
        """
        # Get providers
        providers = self.db.query(OAuthProvider).all()
        
        # Return providers
        return [self._provider_to_dto(provider) for provider in providers]
    
    def get_oauth_provider(self, provider_id: str) -> OAuthProviderDTO:
        """
        Get OAuth provider.
        
        Args:
            provider_id (str): Provider ID
            
        Returns:
            OAuthProviderDTO: OAuth provider
            
        Raises:
            Exception: If provider not found
        """
        # Get provider
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.id == provider_id).first()
        
        # Check if provider exists
        if not provider:
            raise Exception("Provider not found")
        
        # Return provider
        return self._provider_to_dto(provider)
    
    def get_oauth_url(self, request_data: OAuthRequestDTO) -> str:
        """
        Get OAuth authorization URL.
        
        Args:
            request_data (OAuthRequestDTO): Request data
            
        Returns:
            str: Authorization URL
            
        Raises:
            Exception: If provider not found
        """
        # Get provider
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.id == request_data.provider_id).first()
        
        # Check if provider exists
        if not provider:
            raise Exception("Provider not found")
        
        # Create adapter
        adapter = self.adapter_factory.create_adapter(provider.type)
        
        # Get authorization URL
        auth_url = adapter.get_auth_url(
            provider=provider,
            redirect_uri=request_data.redirect_uri,
            state=request_data.state
        )
        
        return auth_url
    
    def handle_oauth_callback(self, callback_data: OAuthCallbackDTO, user_id: str) -> ExternalToolConnectionDTO:
        """
        Handle OAuth callback.
        
        Args:
            callback_data (OAuthCallbackDTO): Callback data
            user_id (str): User ID
            
        Returns:
            ExternalToolConnectionDTO: External tool connection
            
        Raises:
            Exception: If provider not found or error in callback
        """
        # Check if there's an error in callback
        if callback_data.error:
            raise Exception(f"OAuth error: {callback_data.error}")
        
        # Get provider
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.id == callback_data.provider_id).first()
        
        # Check if provider exists
        if not provider:
            raise Exception("Provider not found")
        
        # Create adapter
        adapter = self.adapter_factory.create_adapter(provider.type)
        
        # Exchange code for token
        token_data = adapter.exchange_code_for_token(
            provider=provider,
            code=callback_data.code
        )
        
        # Get user info
        user_info = adapter.get_user_info(
            provider=provider,
            access_token=token_data["access_token"]
        )
        
        # Check if connection already exists
        existing_connection = self.db.query(ExternalToolConnection).filter(
            ExternalToolConnection.user_id == user_id,
            ExternalToolConnection.provider_id == provider.id,
            ExternalToolConnection.account_id == str(user_info["id"])
        ).first()
        
        if existing_connection:
            # Update existing connection
            existing_connection.access_token = token_data["access_token"]
            existing_connection.refresh_token = token_data.get("refresh_token")
            existing_connection.token_type = token_data.get("token_type")
            existing_connection.scope = token_data.get("scope")
            existing_connection.account_name = user_info.get("name")
            existing_connection.account_email = user_info.get("email")
            existing_connection.is_active = True
            existing_connection.metadata = user_info
            existing_connection.last_used_at = datetime.utcnow()
            existing_connection.expires_at = datetime.fromisoformat(token_data["expires_at"]) if "expires_at" in token_data else None
            existing_connection.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(existing_connection)
            
            return self._connection_to_dto(existing_connection)
        
        # Create connection
        connection = ExternalToolConnection(
            user_id=user_id,
            provider_id=provider.id,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_type=token_data.get("token_type"),
            scope=token_data.get("scope"),
            account_name=user_info.get("name"),
            account_email=user_info.get("email"),
            account_id=str(user_info["id"]),
            is_active=True,
            metadata=user_info,
            last_used_at=datetime.utcnow(),
            expires_at=datetime.fromisoformat(token_data["expires_at"]) if "expires_at" in token_data else None
        )
        
        # Add connection to database
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        
        # Return connection
        return self._connection_to_dto(connection)
    
    def create_connection(self, connection_data: ExternalToolConnectionCreateDTO, user_id: str) -> ExternalToolConnectionDTO:
        """
        Create external tool connection.
        
        Args:
            connection_data (ExternalToolConnectionCreateDTO): Connection data
            user_id (str): User ID
            
        Returns:
            ExternalToolConnectionDTO: Created connection
            
        Raises:
            Exception: If provider not found
        """
        # Get provider
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.id == connection_data.provider_id).first()
        
        # Check if provider exists
        if not provider:
            raise Exception("Provider not found")
        
        # Create adapter
        adapter = self.adapter_factory.create_adapter(provider.type)
        
        # Get user info
        user_info = adapter.get_user_info(
            provider=provider,
            access_token=connection_data.access_token
        )
        
        # Check if connection already exists
        existing_connection = self.db.query(ExternalToolConnection).filter(
            ExternalToolConnection.user_id == user_id,
            ExternalToolConnection.provider_id == provider.id,
            ExternalToolConnection.account_id == str(user_info["id"])
        ).first()
        
        if existing_connection:
            # Update existing connection
            existing_connection.access_token = connection_data.access_token
            existing_connection.refresh_token = connection_data.refresh_token
            existing_connection.account_name = connection_data.account_name or user_info.get("name")
            existing_connection.account_email = connection_data.account_email or user_info.get("email")
            existing_connection.is_active = True
            existing_connection.metadata = connection_data.metadata or user_info
            existing_connection.last_used_at = datetime.utcnow()
            existing_connection.expires_at = connection_data.expires_at
            existing_connection.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(existing_connection)
            
            return self._connection_to_dto(existing_connection)
        
        # Create connection
        connection = ExternalToolConnection(
            user_id=user_id,
            provider_id=provider.id,
            access_token=connection_data.access_token,
            refresh_token=connection_data.refresh_token,
            account_name=connection_data.account_name or user_info.get("name"),
            account_email=connection_data.account_email or user_info.get("email"),
            account_id=connection_data.account_id or str(user_info["id"]),
            is_active=True,
            metadata=connection_data.metadata or user_info,
            last_used_at=datetime.utcnow(),
            expires_at=connection_data.expires_at
        )
        
        # Add connection to database
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        
        # Return connection
        return self._connection_to_dto(connection)
    
    def get_user_connections(self, user_id: str) -> List[ExternalToolConnectionDTO]:
        """
        Get connections for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            List[ExternalToolConnectionDTO]: List of connections
        """
        # Get connections
        connections = self.db.query(ExternalToolConnection).filter(
            ExternalToolConnection.user_id == user_id
        ).all()
        
        # Return connections
        return [self._connection_to_dto(connection) for connection in connections]
    
    def get_connection(self, connection_id: str, user_id: str) -> ExternalToolConnectionDTO:
        """
        Get a connection.
        
        Args:
            connection_id (str): Connection ID
            user_id (str): User ID
            
        Returns:
            ExternalToolConnectionDTO: Connection
            
        Raises:
            Exception: If connection not found or user does not have permission
        """
        # Get connection
        connection = self.db.query(ExternalToolConnection).filter(
            ExternalToolConnection.id == connection_id,
            ExternalToolConnection.user_id == user_id
        ).first()
        
        # Check if connection exists
        if not connection:
            raise Exception("Connection not found or user does not have permission")
        
        # Return connection
        return self._connection_to_dto(connection)
    
    def refresh_connection(self, connection_id: str, user_id: str) -> ExternalToolConnectionDTO:
        """
        Refresh connection token.
        
        Args:
            connection_id (str): Connection ID
            user_id (str): User ID
            
        Returns:
            ExternalToolConnectionDTO: Updated connection
            
        Raises:
            Exception: If connection not found, user does not have permission, or refresh token not available
        """
        # Get connection
        connection = self.db.query(ExternalToolConnection).filter(
            ExternalToolConnection.id == connection_id,
            ExternalToolConnection.user_id == user_id
        ).first()
        
        # Check if connection exists
        if not connection:
            raise Exception("Connection not found or user does not have permission")
        
        # Check if refresh token is available
        if not connection.refresh_token:
            raise Exception("Refresh token not available")
        
        # Get provider
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.id == connection.provider_id).first()
        
        # Create adapter
        adapter = self.adapter_factory.create_adapter(provider.type)
        
        # Refresh token
        token_data = adapter.refresh_token(
            provider=provider,
            refresh_token=connection.refresh_token
        )
        
        # Update connection
        connection.access_token = token_data["access_token"]
        connection.refresh_token = token_data.get("refresh_token", connection.refresh_token)
        connection.token_type = token_data.get("token_type", connection.token_type)
        connection.scope = token_data.get("scope", connection.scope)
        connection.last_used_at = datetime.utcnow()
        connection.expires_at = datetime.fromisoformat(token_data["expires_at"]) if "expires_at" in token_data else None
        connection.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(connection)
        
        # Return connection
        return self._connection_to_dto(connection)
    
    def revoke_connection(self, connection_id: str, user_id: str) -> Dict[str, Any]:
        """
        Revoke connection.
        
        Args:
            connection_id (str): Connection ID
            user_id (str): User ID
            
        Returns:
            Dict[str, Any]: Success response
            
        Raises:
            Exception: If connection not found or user does not have permission
        """
        # Get connection
        connection = self.db.query(ExternalToolConnection).filter(
            ExternalToolConnection.id == connection_id,
            ExternalToolConnection.user_id == user_id
        ).first()
        
        # Check if connection exists
        if not connection:
            raise Exception("Connection not found or user does not have permission")
        
        # Get provider
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.id == connection.provider_id).first()
        
        # Create adapter
        adapter = self.adapter_factory.create_adapter(provider.type)
        
        # Revoke token
        try:
            adapter.revoke_token(
                provider=provider,
                access_token=connection.access_token
            )
        except Exception as e:
            # Log error but continue
            print(f"Error revoking token: {e}")
        
        # Update connection
        connection.is_active = False
        connection.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Return success response
        return {"message": "Connection revoked successfully"}
    
    def delete_connection(self, connection_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete connection.
        
        Args:
            connection_id (str): Connection ID
            user_id (str): User ID
            
        Returns:
            Dict[str, Any]: Success response
            
        Raises:
            Exception: If connection not found or user does not have permission
        """
        # Get connection
        connection = self.db.query(ExternalToolConnection).filter(
            ExternalToolConnection.id == connection_id,
            ExternalToolConnection.user_id == user_id
        ).first()
        
        # Check if connection exists
        if not connection:
            raise Exception("Connection not found or user does not have permission")
        
        # Get provider
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.id == connection.provider_id).first()
        
        # Create adapter
        adapter = self.adapter_factory.create_adapter(provider.type)
        
        # Revoke token
        try:
            adapter.revoke_token(
                provider=provider,
                access_token=connection.access_token
            )
        except Exception as e:
            # Log error but continue
            print(f"Error revoking token: {e}")
        
        # Delete connection
        self.db.delete(connection)
        self.db.commit()
        
        # Return success response
        return {"message": "Connection deleted successfully"}
    
    def _provider_to_dto(self, provider: OAuthProvider) -> OAuthProviderDTO:
        """
        Convert OAuthProvider model to OAuthProviderDTO.
        
        Args:
            provider (OAuthProvider): OAuthProvider model
            
        Returns:
            OAuthProviderDTO: OAuthProvider DTO
        """
        return OAuthProviderDTO(
            id=provider.id,
            name=provider.name,
            type=provider.type,
            auth_url=provider.auth_url,
            token_url=provider.token_url,
            scope=provider.scope,
            client_id=provider.client_id,
            redirect_uri=provider.redirect_uri,
            additional_params=provider.additional_params
        )
    
    def _connection_to_dto(self, connection: ExternalToolConnection) -> ExternalToolConnectionDTO:
        """
        Convert ExternalToolConnection model to ExternalToolConnectionDTO.
        
        Args:
            connection (ExternalToolConnection): ExternalToolConnection model
            
        Returns:
            ExternalToolConnectionDTO: ExternalToolConnection DTO
        """
        # Get provider
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.id == connection.provider_id).first()
        
        return ExternalToolConnectionDTO(
            id=connection.id,
            user_id=connection.user_id,
            provider_id=connection.provider_id,
            provider_type=provider.type if provider else ExternalToolType.CUSTOM,
            account_name=connection.account_name,
            account_email=connection.account_email,
            account_id=connection.account_id,
            is_active=connection.is_active,
            metadata=connection.metadata,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
            last_used_at=connection.last_used_at,
            expires_at=connection.expires_at
        )