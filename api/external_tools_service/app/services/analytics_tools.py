import requests
import json
from typing import Optional, Dict, Any
from api.shared.utils.supabase import SupabaseManager

def get_metabase_card_data(card_id: int, session_token: str, metabase_url: str, supabase_bucket: Optional[str] = None, supabase_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Obtiene datos de una tarjeta (dashboard) de Metabase y opcionalmente guarda el resultado en Supabase Storage.
    """
    headers = {"X-Metabase-Session": session_token}
    try:
        response = requests.get(f"{metabase_url}/api/card/{card_id}/query/json", headers=headers)
        if response.status_code == 200:
            result = response.json()
            if supabase_bucket and supabase_path:
                supabase = SupabaseManager().get_client()
                supabase.storage().from_(supabase_bucket).upload(supabase_path, json.dumps(result), {"content-type": "application/json"})
            return result
        else:
            return None
    except Exception as e:
        print(f"Metabase error: {e}")
        return None 