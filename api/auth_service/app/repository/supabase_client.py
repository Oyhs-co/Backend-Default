import os
from typing import Any

from supabase import create_client


class SupabaseClient:
    _instance = None

    def __new__(cls) -> Any:
        if cls._instance is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            cls._instance = create_client(url, key)
        return cls._instance
