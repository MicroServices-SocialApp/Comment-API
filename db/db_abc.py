# from sqlalchemy import select, update as sql_update, delete as sql_delete
from schemas.schemas_abc import AbcDisplay, AbcModel
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.models import DbAbc


async def create(
    request: AbcModel,
    db: AsyncSession,
) -> AbcDisplay:

    new_abc = DbAbc(
        abc=request.abc,
    )
    db.add(new_abc)
    await db.commit()
    return AbcDisplay.model_validate(new_abc)


# --------------------------------------------------------------------------
