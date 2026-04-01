from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import asyncio

from src.api.webhooks import router as webhooks_router
from src.services.dispatcher import process_outbox

async def dispatcher_loop():
    while True:
        await process_outbox()
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(dispatcher_loop())
    yield
    task.cancel()

app = FastAPI(
    title="Product Price Monitoring API",
    description="Real-time tracking of marketplace product pricing and availability.",
    lifespan=lifespan
)

app.include_router(webhooks_router)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": "Validation failed", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "Internal server error"}
    )

@app.get("/health")
def health_check():
    return {"success": True, "message": "API is healthy"}
