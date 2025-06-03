import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables
load_dotenv(".env")

# Supabase configuration
# Provide default empty strings if a variable is not found, though create_client will likely fail.
# A better approach would be to raise an error if these are not set.
SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")


class SupabaseManager:
    """Singleton class for managing Supabase client"""

    _instance = None
    client: Client

    def __new__(cls) -> Any:
        if cls._instance is None:
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_KEY must be set in .env. Please check your environment configuration."
                )
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            # Now we are sure SUPABASE_URL and SUPABASE_KEY are strings
            cls._instance.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return cls._instance

    def get_client(self) -> Client:
        """
        Get Supabase client.

        Returns:
            Client: Supabase client
        """
        return self.client

    def auth(self) -> Any:
        """
        Get Supabase auth client.

        Returns:
            Auth: Supabase auth client
        """
        return self.client.auth

    def storage(self) -> Any:
        """
        Get Supabase storage client.

        Returns:
            Storage: Supabase storage client
        """
        return self.client.storage

    def table(self, table_name: str) -> Any:
        """
        Get Supabase table client.

        Args:
            table_name (str): Table name

        Returns:
            Table: Supabase table client
        """
        return self.client.table(table_name)

    def sign_up(
        self, email: str, password: str, user_metadata: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Sign up a new user.

        Args:
            email (str): User email
            password (str): User password
            user_metadata (Dict[str, Any], optional): User metadata

        Returns:
            Dict: Supabase auth response
        """
        return self.auth().sign_up(
            {"email": email, "password": password, "options": {"data": user_metadata}}
        )

    def sign_in(self, email: str, password: str) -> Any:
        """
        Sign in a user.

        Args:
            email (str): User email
            password (str): User password

        Returns:
            Dict: Supabase auth response
        """
        return self.auth().sign_in_with_password({"email": email, "password": password})

    def sign_out(self, access_token: str) -> Any:
        """
        Sign out a user.

        Args:
            access_token (str): Access token

        Returns:
            Dict: Supabase auth response
        """
        return self.auth().sign_out()

    def get_user(self, access_token: str) -> Any:
        """
        Get user information.

        Args:
            access_token (str): Access token

        Returns:
            Dict: User information
        """
        return self.auth().get_user(jwt=access_token)

    def refresh_token(self, refresh_token: str) -> Any:
        """
        Refresh JWT token.

        Args:
            refresh_token (str): Refresh token

        Returns:
            Dict: Supabase auth response
        """
        return self.auth().refresh_session(refresh_token=refresh_token)

    def create_bucket(self, bucket_name: str) -> Any:
        """
        Create a storage bucket.

        Args:
            bucket_name (str): Bucket name

        Returns:
            Dict: Supabase storage response
        """
        return self.storage().create_bucket(bucket_name)

    def upload_file(
        self, bucket_name: str, file_path: str, file_content: Any, content_type: str
    ) -> Any:
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
        return (
            self.storage()
            .from_(bucket_name)
            .upload(file_path, file_content, {"content-type": content_type})
        )

    def get_file_url(self, bucket_name: str, file_path: str) -> Any:
        """
        Get file URL.

        Args:
            bucket_name (str): Bucket name
            file_path (str): File path in the bucket

        Returns:
            str: File URL
        """
        return self.storage().from_(bucket_name).get_public_url(file_path)

    def delete_file(self, bucket_name: str, file_path: str) -> Any:
        """
        Delete a file from storage.

        Args:
            bucket_name (str): Bucket name
            file_path (str): File path in the bucket

        Returns:
            Dict: Supabase storage response
        """
        return self.storage().from_(bucket_name).remove([file_path])
