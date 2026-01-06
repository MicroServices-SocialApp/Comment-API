from typing import Optional
from pydantic import BaseModel, Field


class AbcModel(BaseModel):
    abc: str = Field(
        default=Ellipsis,
        description="New password. Will be re-hashed.",
        deprecated=False,
        json_schema_extra={"example": "SecurePassword456!"},
        min_length=2,
        max_length=40,
    )
    
class AbcPatchModel(BaseModel):
    abc: Optional[str] = Field(
        default=None,
        description="New password if a change is desired. Will be re-hashed.",
        deprecated=False,
        json_schema_extra={"example": "NewSecurePassword456!"},
        min_length=2,
        max_length=40,
    )
#--------------------------------------------------------------------------

class AbcDisplay(BaseModel):
    id: int
    abc: str
    
    class ConfigDict:
        from_attributes = True
