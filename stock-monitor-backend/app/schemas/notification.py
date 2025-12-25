from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class NotificationConfigResponse(BaseModel):
    id: int
    user_id: int
    api_url: Optional[str] = None
    api_method: str
    is_enabled: bool

    class Config:
        from_attributes = True

class NotificationConfigUpdate(BaseModel):
    api_url: Optional[str] = None
    api_headers: Optional[Dict[str, str]] = None
    api_method: Optional[str] = None
    is_enabled: Optional[bool] = None
