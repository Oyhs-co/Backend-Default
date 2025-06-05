import os
import requests
from typing import Optional
from api.shared.utils.supabase import SupabaseManager

def process_document_with_libreoffice(file_path: str, output_format: str = "pdf", supabase_bucket: Optional[str] = None, supabase_path: Optional[str] = None) -> Optional[str]:
    """
    Envía un documento a LibreOffice Online para conversión y opcionalmente lo sube a Supabase Storage.
    Retorna la URL pública si se sube a Supabase, o None si falla.
    """
    lool_url = os.getenv("LIBREOFFICE_ONLINE_URL", "http://localhost:9980/lool/convert-to/")
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{lool_url}{output_format}", files=files)
        if response.status_code == 200:
            if supabase_bucket and supabase_path:
                supabase = SupabaseManager().get_client()
                supabase.storage().from_(supabase_bucket).upload(supabase_path, response.content, {"content-type": f"application/{output_format}"})
                url = supabase.storage().from_(supabase_bucket).get_public_url(supabase_path)
                return url
            return None
        else:
            return None
    except Exception as e:
        print(f"LibreOffice error: {e}")
        return None 