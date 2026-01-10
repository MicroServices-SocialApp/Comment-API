from pydantic import BaseModel, ConfigDict, Field, field_serializer
from datetime import datetime


class CommentModel(BaseModel):
    post_id: int = Field(
        default=Ellipsis,
        description="The id of the post where the comment is written",
        deprecated=False,
        json_schema_extra={"example": 1},
        min_length=None,
        max_length=None,
    )
    
    text: str = Field(
        default=Ellipsis,
        description="The text/string of the comment",
        deprecated=False,
        json_schema_extra={"example": "Really cool post"},
        min_length=None,
        max_length=256,
    )

class CommentUpdateModel(BaseModel):
    text: str = Field(
        default=Ellipsis,
        description="New text/string of the comment if a change is desired.",
        deprecated=False,
        json_schema_extra={"example": "This post sucks and so do you buddy."},
        min_length=0,
        max_length=256,
    )

class CommentPatchModel(BaseModel):
    text: str | None = Field(
        default=None,
        description="New text/string of the comment if a change is desired.",
        deprecated=False,
        json_schema_extra={"example": "This post sucks and so do you buddy."},
        min_length=0,
        max_length=256,
    )
    
#--------------------------------------------------------------------------

class CommentDisplay(BaseModel):
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