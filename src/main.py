import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import asyncio

from src.api.webhooks import router as webhooks_router
from src.api.refresh import router as refresh_router
from src.api.products import router as products_router
from src.api.analytics import router as analytics_router
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

# Securely allow local file/UI testing 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For purely local dev evaluation purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhooks_router)
app.include_router(refresh_router)
app.include_router(products_router)
app.include_router(analytics_router)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
