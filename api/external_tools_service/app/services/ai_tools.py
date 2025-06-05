import os
import requests
import json
from typing import Optional, Dict, Any
from api.shared.utils.supabase import SupabaseManager

def query_huggingface(model: str, payload: Dict[str, Any], supabase_bucket: Optional[str] = None, supabase_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Consulta la API de Hugging Face para inferencia de modelos y opcionalmente guarda el resultado en Supabase Storage.
    """
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    headers = {"Authorization": f"Bearer {hf_token}"}
    try:
        response = requests.post(f"https://api-inference.huggingface.co/models/{model}", headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if supabase_bucket and supabase_path:
                supabase = SupabaseManager().get_client()
                supabase.storage().from_(supabase_bucket).upload(supabase_path, json.dumps(result), {"content-type": "application/json"})
            return result
        else:
            return None
    except Exception as e:
        print(f"HuggingFace error: {e}")
        return None 