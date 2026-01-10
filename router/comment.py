from schemas.schemas_comment import (
    CommentModel,
    CommentDisplay,
    CommentPatchModel,
    CommentUpdateModel,
)
from schemas.schemas_paginated_comment import PaginatedCommentDisplay
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, Path, status
from auth.oauth2 import get_current_user_id
from db.database import get_async_db
from typing import Annotated
from pydantic import Field
from db import db_comment

router = APIRouter(prefix="/comment", tags=["comment"])

CommentIdPath = Annotated[
    int,
    Path(
        description="The unique ID of the comment",
        gt=0,
        json_schema_extra={"example": 1},
    ),
]

CurrentUser = Annotated[
    int,
    Field(
        description="The unique ID of the user",
        gt=0,
        json_schema_extra={"example": 1},
    ),
]


@router.post(
    "/create",
    summary="une phrase qui resume la fonction.",
    description="une decription longue et precise",
    status_code=status.HTTP_201_CREATED,
)
async def create(
    request: CommentModel,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: CurrentUser = Depends(get_current_user_id),
) -> CommentDisplay:
    comment: CommentDisplay = await db_comment.create(request, db, current_user_id)
    return comment


# --------------------------------------------------------------------------


@router.get(
    "/read_all",
    summary="Retrieve all comments",
    description="Returns a complete list of all comments stored in the PostgreSQL database.",
)
async def read_all(
    limit: int = 10,
    last_id: int | None = None,
    db: AsyncSession = Depends(get_async_db),
) -> PaginatedCommentDisplay:
    comment: PaginatedCommentDisplay = await db_comment.read_all(limit, last_id, db)
    return comment


# --------------------------------------------------------------------------


@router.put(
    "/update/{comment_id}",
    summary="Update an existing comment",
    description="Perform a full update of a comment's information. All fields in the request body are required.",
)
async def update(
    comment_id: CommentIdPath,
    request: CommentUpdateModel,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: CurrentUser = Depends(get_current_user_id),
) -> CommentDisplay:
    comment: CommentDisplay = await db_comment.update(
        comment_id, request, db, current_user_id
    )
    return comment


# --------------------------------------------------------------------------


@router.patch(
    "/patch/{comment_id}",
    summary="Partially update a comment",
    description="Update specific fields of a comment record without affecting the others.",
)
async def patch(
    comment_id: CommentIdPath,
    request: CommentPatchModel,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: CurrentUser = Depends(get_current_user_id),
) -> CommentDisplay:
    comment: CommentDisplay = await db_comment.patch(
        comment_id, request, db, current_user_id
    )
    return comment


# --------------------------------------------------------------------------


@router.delete(
    "/delete/{comment_id}",
    summary="Delete a comment from the database",
    description="Permanently removes a comment record from the PostgreSQL database using their unique ID.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(
    comment_id: CommentIdPath,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: CurrentUser = Depends(get_current_user_id),
) -> None:
    await db_comment.delete(comment_id, db, current_user_id)
    return None
