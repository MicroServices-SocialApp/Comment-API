from fastapi import APIRouter, Depends, status
from db import db_abc
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.database import get_async_db
from schemas.schemas_abc import AbcModel, AbcDisplay

router = APIRouter(prefix="/abc", tags=["abc"])


@router.post(
    "/create",
    include_in_schema=True,
    deprecated=False,
    name="Abc_Creation",
    summary="une phrase qui resume la fonction.",
    description="une decription longue et precise",
    response_model=AbcDisplay,
    status_code=status.HTTP_201_CREATED,
    response_description="Succes de la reponse",
    responses={
        201: {
            "description": "SUCCESS - abc has been created",
            "content": {
                "application/json": {"example": {"id": 1, "abc": "abc"}},
            },
        },
        409: {"description": "CONFLICT"},
    },
)
async def create(
    request: AbcModel,
    db: AsyncSession = Depends(get_async_db),
) -> AbcDisplay:
    abc: AbcDisplay = await db_abc.create(request, db)
    return abc


# --------------------------------------------------------------------------
