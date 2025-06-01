from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
from datetime import datetime, timedelta

from api.shared.models.external_tools import OAuthProvider, ExternalToolConnection
from api.external-tools-service.app.schemas.external_tools import ExternalToolType


class OAuthAdapter(ABC):
    """Abstract adapter for OAuth providers"""
    
    @abstractmethod
    def get_auth_url(self, provider: OAuthProvider, redirect_uri: Optional[str] = None, state: Optional[str] = None) -> str:
        """
        Get authorization URL.
        
        Args:
            provider (OAuthProvider): OAuth provider
            redirect_uri (Optional[str], optional): Redirect URI. Defaults to None.
            state (Optional[str], optional): State. Defaults to None.
            
        Returns:
            str: Authorization URL
        """
        pass
    
    @abstractmethod
    def exchange_code_for_token(self, provider: OAuthProvider, code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            provider (OAuthProvider): OAuth provider
            code (str): Authorization code
            redirect_uri (Optional[str], optional): Redirect URI. Defaults to None.
            
        Returns:
            Dict[str, Any]: Token response
        """
        pass
    
    @abstractmethod
    def refresh_token(self, provider: OAuthProvider, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token.
        
        Args:
            provider (OAuthProvider): OAuth provider
            refresh_token (str): Refresh token
            
        Returns:
            Dict[str, Any]: Token response
        """
        pass
    
    @abstractmethod
    def get_user_info(self, provider: OAuthProvider, access_token: str) -> Dict[str, Any]:
        """
        Get user information.
        
        Args:
            provider (OAuthProvider): OAuth provider
            access_token (str): Access token
            
        Returns:
            Dict[str, Any]: User information
        """
        pass
    
    @abstractmethod
    def revoke_token(self, provider: OAuthProvider, access_token: str) -> bool:
        """
        Revoke access token.
        
        Args:
            provider (OAuthProvider): OAuth provider
            access_token (str): Access token
            
        Returns:
            bool: True if token was revoked, False otherwise
        """
        pass


class GitHubOAuthAdapter(OAuthAdapter):
    """Adapter for GitHub OAuth"""
    
    def get_auth_url(self, provider: OAuthProvider, redirect_uri: Optional[str] = None, state: Optional[str] = None) -> str:
        """
        Get GitHub authorization URL.
        
        Args:
            provider (OAuthProvider): OAuth provider
            redirect_uri (Optional[str], optional): Redirect URI. Defaults to None.
            state (Optional[str], optional): State. Defaults to None.
            
        Returns:
            str: Authorization URL
        """
        # Use provider's redirect URI if not specified
        if not redirect_uri:
            redirect_uri = provider.redirect_uri
        
        # Build authorization URL
        auth_url = f"{provider.auth_url}?client_id={provider.client_id}&redirect_uri={redirect_uri}&scope={provider.scope}"
        
        # Add state if provided
        if state:
            auth_url += f"&state={state}"
        
        # Add additional parameters if any
        if provider.additional_params:
            for key, value in provider.additional_params.items():
                auth_url += f"&{key}={value}"
        
        return auth_url
    
    def exchange_code_for_token(self, provider: OAuthProvider, code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchange GitHub authorization code for access token.
        
        Args:
            provider (OAuthProvider): OAuth provider
            code (str): Authorization code
            redirect_uri (Optional[str], optional): Redirect URI. Defaults to None.
            
        Returns:
            Dict[str, Any]: Token response
        """
        # Use provider's redirect URI if not specified
        if not redirect_uri:
            redirect_uri = provider.redirect_uri
        
        # Prepare request data
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        # Add additional parameters if any
        if provider.additional_params:
            data.update(provider.additional_params)
        
        # Make request
        headers = {"Accept": "application/json"}
        response = requests.post(provider.token_url, data=data, headers=headers)
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to exchange code for token: {response.text}")
        
        # Parse response
        token_data = response.json()
        
        # Add expiration time if not provided
        if "expires_in" in token_data:
            expires_in = token_data["expires_in"]
            token_data["expires_at"] = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
        
        return token_data
    
    def refresh_token(self, provider: OAuthProvider, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh GitHub access token.
        
        Args:
            provider (OAuthProvider): OAuth provider
            refresh_token (str): Refresh token
            
        Returns:
            Dict[str, Any]: Token response
        """
        # GitHub doesn't support refresh tokens for OAuth Apps
        # For GitHub Apps, you would implement this
        raise NotImplementedError("GitHub OAuth Apps do not support refresh tokens")
    
    def get_user_info(self, provider: OAuthProvider, access_token: str) -> Dict[str, Any]:
        """
        Get GitHub user information.
        
        Args:
            provider (OAuthProvider): OAuth provider
            access_token (str): Access token
            
        Returns:
            Dict[str, Any]: User information
        """
        # Make request
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/json"
        }
        response = requests.get("https://api.github.com/user", headers=headers)
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")
        
        # Parse response
        user_info = response.json()
        
        return {
            "id": user_info.get("id"),
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "avatar_url": user_info.get("avatar_url"),
            "html_url": user_info.get("html_url")
        }
    
    def revoke_token(self, provider: OAuthProvider, access_token: str) -> bool:
        """
        Revoke GitHub access token.
        
        Args:
            provider (OAuthProvider): OAuth provider
            access_token (str): Access token
            
        Returns:
            bool: True if token was revoked, False otherwise
        """
        # Make request
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/json"
        }
        response = requests.delete(
            f"https://api.github.com/applications/{provider.client_id}/token",
            auth=(provider.client_id, provider.client_secret),
            json={"access_token": access_token},
            headers=headers
        )
        
        # Check response
        return response.status_code == 204


class GoogleOAuthAdapter(OAuthAdapter):
    """Adapter for Google OAuth"""
    
    def get_auth_url(self, provider: OAuthProvider, redirect_uri: Optional[str] = None, state: Optional[str] = None) -> str:
        """
        Get Google authorization URL.
        
        Args:
            provider (OAuthProvider): OAuth provider
            redirect_uri (Optional[str], optional): Redirect URI. Defaults to None.
            state (Optional[str], optional): State. Defaults to None.
            
        Returns:
            str: Authorization URL
        """
        # Use provider's redirect URI if not specified
        if not redirect_uri:
            redirect_uri = provider.redirect_uri
        
        # Build authorization URL
        auth_url = f"{provider.auth_url}?client_id={provider.client_id}&redirect_uri={redirect_uri}&scope={provider.scope}&response_type=code&access_type=offline&prompt=consent"
        
        # Add state if provided
        if state:
            auth_url += f"&state={state}"
        
        # Add additional parameters if any
        if provider.additional_params:
            for key, value in provider.additional_params.items():
                auth_url += f"&{key}={value}"
        
        return auth_url
    
    def exchange_code_for_token(self, provider: OAuthProvider, code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchange Google authorization code for access token.
        
        Args:
            provider (OAuthProvider): OAuth provider
            code (str): Authorization code
            redirect_uri (Optional[str], optional): Redirect URI. Defaults to None.
            
        Returns:
            Dict[str, Any]: Token response
        """
        # Use provider's redirect URI if not specified
        if not redirect_uri:
            redirect_uri = provider.redirect_uri
        
        # Prepare request data
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        # Make request
        response = requests.post(provider.token_url, data=data)
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to exchange code for token: {response.text}")
        
        # Parse response
        token_data = response.json()
        
        # Add expiration time
        if "expires_in" in token_data:
            expires_in = token_data["expires_in"]
            token_data["expires_at"] = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
        
        return token_data
    
    def refresh_token(self, provider: OAuthProvider, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh Google access token.
        
        Args:
            provider (OAuthProvider): OAuth provider
            refresh_token (str): Refresh token
            
        Returns:
            Dict[str, Any]: Token response
        """
        # Prepare request data
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        # Make request
        response = requests.post(provider.token_url, data=data)
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
        
        # Parse response
        token_data = response.json()
        
        # Add expiration time
        if "expires_in" in token_data:
            expires_in = token_data["expires_in"]
            token_data["expires_at"] = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
        
        # Add refresh token (Google doesn't return it in refresh response)
        token_data["refresh_token"] = refresh_token
        
        return token_data
    
    def get_user_info(self, provider: OAuthProvider, access_token: str) -> Dict[str, Any]:
        """
        Get Google user information.
        
        Args:
            provider (OAuthProvider): OAuth provider
            access_token (str): Access token
            
        Returns:
            Dict[str, Any]: User information
        """
        # Make request
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")
        
        # Parse response
        user_info = response.json()
        
        return {
            "id": user_info.get("sub"),
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "picture": user_info.get("picture")
        }
    
    def revoke_token(self, provider: OAuthProvider, access_token: str) -> bool:
        """
        Revoke Google access token.
        
        Args:
            provider (OAuthProvider): OAuth provider
            access_token (str): Access token
            
        Returns:
            bool: True if token was revoked, False otherwise
        """
        # Make request
        response = requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": access_token},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Check response
        return response.status_code == 200


class OAuthAdapterFactory:
    """Factory for creating OAuth adapters"""
    
    def create_adapter(self, provider_type: ExternalToolType) -> OAuthAdapter:
        """
        Create OAuth adapter based on provider type.
        
        Args:
            provider_type (ExternalToolType): Provider type
            
        Returns:
            OAuthAdapter: OAuth adapter
            
        Raises:
            ValueError: If provider type is not supported
        """
        if provider_type == ExternalToolType.GITHUB:
            return GitHubOAuthAdapter()
        elif provider_type == ExternalToolType.GOOGLE_DRIVE:
            return GoogleOAuthAdapter()
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")