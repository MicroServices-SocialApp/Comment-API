from sqlalchemy import (
    CursorResult,
    Delete,
    select,
    update as sql_update,
    delete as sql_delete,
)
from schemas.schemas_comment import (
    CommentModel,
    CommentDisplay,
    CommentPatchModel,
    CommentUpdateModel,
)
from schemas.schemas_paginated_comment import Comments, PaginatedCommentDisplay
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from db.models import DbComment


async def create(
    request: CommentModel,
    db: AsyncSession,
    current_user_id: int,
) -> CommentDisplay:
    """Creates a new comment and associates it with a user and a post.

    This function initializes a database model using the request data and
    the authenticated user's ID, persists it to the database, and returns
    the validated display schema.

    Args:
        request (CommentModel): The incoming data containing post_id and text.
        db (AsyncSession): The asynchronous database session.
        current_user_id (int): The ID of the user creating the comment.

    Returns:
        CommentDisplay: The newly created comment, including auto-generated
            fields like ID and timestamps.
    """

    new_comment = DbComment(
        user_id=current_user_id,
        post_id=request.post_id,
        text=request.text,
    )
    db.add(new_comment)
    await db.commit()
    return CommentDisplay.model_validate(new_comment)


# --------------------------------------------------------------------------


async def read_all(
    limit: int,
    last_id: int | None,
    db: AsyncSession,
) -> PaginatedCommentDisplay:
    """Retrieves a paginated list of comments using keyset pagination.

    This function fetches one extra record beyond the limit to determine if
    there are more pages. It uses the comment ID as a cursor for efficient
    sorting and filtering.

    Args:
        limit (int): The maximum number of comments to return per page.
        last_id (int | None): The ID of the last comment from the previous page.
            Used as the cursor for fetching the next set of results.
        db (AsyncSession): The asynchronous database session.

    Returns:
        PaginatedCommentDisplay: A schema containing the list of comments,
             the next_cursor, and a boolean indicating if more pages exist.
    """

    if last_id:
        query = (
            select(DbComment)
            .order_by(DbComment.id.desc())
            .limit(limit + 1)
            .where(DbComment.id < last_id)
        )
    else:
        query = select(DbComment).order_by(DbComment.id.desc()).limit(limit + 1)

    result = await db.execute(query)
    comment = result.scalars().all()

    items = comment[:limit]
    next_cursor: int | None = items[-1].id if items else None
    has_more: bool = len(comment) > limit

    return PaginatedCommentDisplay(
        items=[Comments.model_validate(c) for c in items],
        next_cursor=next_cursor if has_more else None,
        has_more=has_more,
    )


# --------------------------------------------------------------------------


async def update(
    comment_id: int,
    request: CommentUpdateModel,
    db: AsyncSession,
    current_user_id: int,
) -> CommentDisplay:
    """Replaces the content of an existing comment.

    This function performs an authorized update of a comment's text. It uses
    the 'returning' clause to fetch the updated record in a single database
    transaction for better performance.

    Args:
        comment_id (int): The ID of the comment to be updated.
        request (CommentModel): The new data for the comment.
        db (AsyncSession): The asynchronous database session.
        current_user_id (int): The ID of the user attempting the update
            (used to verify ownership).

    Returns:
        CommentDisplay: The updated comment record validated against the display schema.

    Raises:
        HTTPException: 404 status if the comment does not exist or if the
            current_user_id does not match the comment's owner_id.
    """

    query = (
        sql_update(DbComment)
        .where(DbComment.id == comment_id, DbComment.user_id == current_user_id)
        .values(text=request.text)
        .returning(DbComment)
    )
    result = await db.execute(query)
    comment: DbComment | None = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No comment with id: {comment_id} not found.",
        )

    await db.commit()
    return CommentDisplay.model_validate(comment)


# --------------------------------------------------------------------------


async def patch(
    comment_id: int,
    request: CommentPatchModel,
    db: AsyncSession,
    current_user_id: int,
) -> CommentDisplay:
    """Updates an existing comment partially.

    This function performs an 'atomic update' by only modifying the fields
    provided in the request. It also enforces ownership by checking the
    current_user_id against the comment's owner_id.

    Args:
        comment_id (int): The unique ID of the comment to update.
        request (CommentPatchModel): The partial data to update (validated by Pydantic).
        db (AsyncSession): The asynchronous database session.
        current_user_id (int): The ID of the user attempting the update.

    Returns:
        CommentDisplay: The updated comment record.

    Raises:
        HTTPException: 404 error if the comment doesn't exist or the user
            doesn't have permission to edit it.
    """

    updated_data = request.model_dump(exclude_unset=True)

    query = (
        sql_update(DbComment)
        .where(
            DbComment.id == comment_id,
            DbComment.user_id == current_user_id,
        )
        .values(**updated_data)  # Unpack the dict into the update query
        .returning(DbComment)
    )

    result = await db.execute(query)
    comment: DbComment | None = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No comment with id: {comment_id} not found.",
        )

    await db.commit()
    return CommentDisplay.model_validate(comment)


# --------------------------------------------------------------------------


async def delete(comment_id: int, db: AsyncSession, current_user_id: int) -> None:
    """Deletes a specific comment from the database.

    The operation only succeeds if the comment exists and belongs to the
    requesting user. If no record matches both the ID and the owner_id,
    no rows are deleted and the function returns silently.

    Args:
        comment_id (int): The unique identifier of the comment to be removed.
        db (AsyncSession): The asynchronous database session.
        current_user_id (int): The ID of the user requesting the deletion
            (for ownership verification).

    Returns:
        None
    """

    query: Delete = sql_delete(DbComment).where(
        DbComment.id == comment_id,
        DbComment.user_id == current_user_id,
    )
    result = await db.execute(query)
    if isinstance(result, CursorResult):
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment either not found or unauthorized",
            )

    await db.commit()
    return None
