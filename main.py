from exc.exceptions import add_exception_handlers
from fastapi import FastAPI
from router import comment

# -----------------------------------------------------------------------------------------------

app = FastAPI()
app.include_router(comment.router)

# -----------------------------------------------------------------------------------------------

add_exception_handlers(app)