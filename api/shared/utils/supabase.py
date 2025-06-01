from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


class SupabaseManager:
    """Singleton class for managing Supabase client"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return cls._instance

    def get_client(self) -> Client:
        """
        Get Supabase client.
        
        Returns:
            Client: Supabase client
        """
        return self.client

    def auth(self):
        """
        Get Supabase auth client.
        
        Returns:
            Auth: Supabase auth client
        """
        return self.client.auth

    def storage(self):
        """
        Get Supabase storage client.
        
        Returns:
            Storage: Supabase storage client
        """
        return self.client.storage

    def table(self, table_name: str):
        """
        Get Supabase table client.
        
        Args:
            table_name (str): Table name
            
        Returns:
            Table: Supabase table client
        """
        return self.client.table(table_name)

    def sign_up(self, email: str, password: str, user_metadata: Optional[Dict[str, Any]] = None):
        """
        Sign up a new user.
        
        Args:
            email (str): User email
            password (str): User password
            user_metadata (Dict[str, Any], optional): User metadata
            
        Returns:
            Dict: Supabase auth response
        """
        return self.auth().sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_metadata
            }
        })

    def sign_in(self, email: str, password: str):
        """
        Sign in a user.
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            Dict: Supabase auth response
        """
        return self.auth().sign_in_with_password({
            "email": email,
            "password": password
        })

    def sign_out(self, jwt: str):
        """
        Sign out a user.
        
        Args:
            jwt (str): JWT token
            
        Returns:
            Dict: Supabase auth response
        """
        # Set the JWT token for the client
        self.client.auth.set_session(jwt)
        return self.auth().sign_out()

    def get_user(self, jwt: str):
        """
        Get user information.
        
        Args:
            jwt (str): JWT token
            
        Returns:
            Dict: User information
        """
        # Set the JWT token for the client
        self.client.auth.set_session(jwt)
        return self.auth().get_user()

    def refresh_token(self, refresh_token: str):
        """
        Refresh JWT token.
        
        Args:
            refresh_token (str): Refresh token
            
        Returns:
            Dict: Supabase auth response
        """
        return self.auth().refresh_session(refresh_token)

    def create_bucket(self, bucket_name: str):
        """
        Create a storage bucket.
        
        Args:
            bucket_name (str): Bucket name
            
        Returns:
            Dict: Supabase storage response
        """
        return self.storage().create_bucket(bucket_name)

    def upload_file(self, bucket_name: str, file_path: str, file_content, content_type: str):
        """
        Upload a file to storage.
        
        Args:
            bucket_name (str): Bucket name
            file_path (str): File path in the bucket
            file_content: File content
            content_type (str): File content type
            
        Returns:
            Dict: Supabase storage response
        """
        return self.storage().from_(bucket_name).upload(
            file_path,
            file_content,
            {"content-type": content_type}
        )

    def get_file_url(self, bucket_name: str, file_path: str):
        """
        Get file URL.
        
        Args:
            bucket_name (str): Bucket name
            file_path (str): File path in the bucket
            
        Returns:
            str: File URL
        """
        return self.storage().from_(bucket_name).get_public_url(file_path)

    def delete_file(self, bucket_name: str, file_path: str):
        """
        Delete a file from storage.
        
        Args:
            bucket_name (str): Bucket name
            file_path (str): File path in the bucket
            
        Returns:
            Dict: Supabase storage response
        """
        return self.storage().from_(bucket_name).remove([file_path])