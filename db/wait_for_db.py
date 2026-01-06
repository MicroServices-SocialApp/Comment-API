import asyncio
import asyncpg
import os
import sys

from dotenv import load_dotenv

async def check_db():

    load_dotenv()
    uri: str | None = os.getenv("DATABASE_URL")
    if uri and uri.startswith("postgresql+asyncpg://"):
        uri = uri.replace("postgresql+asyncpg://", "postgresql://")

# ------------------------------------------------------------------------------------

    retries = 30
    while retries > 0:
        try:
            conn = await asyncpg.connect(uri)
            await conn.close()
            print("Database is ready.")
            sys.exit(0)
        except Exception as e:
            print(f"Waiting for database... ({retries} retries left) {e}")
            print(f"DEBUG: Attempting to connect to {uri}")
            retries -= 1
            await asyncio.sleep(2)
    print("Database connection failed.")
    sys.exit(1)

# ------------------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(check_db())