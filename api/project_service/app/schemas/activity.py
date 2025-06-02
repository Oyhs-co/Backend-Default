from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ActivityLogCreateDTO(BaseModel):
    """DTO for creating an activity log"""

    action: str
    entity_type: str
    entity_id: str
    details: Optional[Dict[str, Any]] = None


class ActivityLogResponseDTO(BaseModel):
    """DTO for activity log response"""

    id: str
    project_id: str
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
