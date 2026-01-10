from pydantic import BaseModel, ConfigDict, field_serializer
from datetime import datetime
from typing import List

class Comments(BaseModel):
    id: int
    user_id: int
    post_id: int
    text: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def format_timestamp(self, dt: datetime) -> str:
        # .strftime converts the datetime object to your specific string format
        return dt.strftime('%Y-%m-%dT%H:%M')

class PaginatedCommentDisplay(BaseModel):
    items: List[Comments]
    next_cursor: int | None
    has_more: bool

    model_config = ConfigDict(from_attributes=True)