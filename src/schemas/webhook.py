from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime

class WebhookCreate(BaseModel):
    target_url: HttpUrl

class WebhookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    target_url: HttpUrl
    is_active: bool
    created_at: datetime
