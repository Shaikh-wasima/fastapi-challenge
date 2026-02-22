import logging
from time import perf_counter

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.response import api_response
from app.db.mongo import close_db, init_db
from app.routers import auth, challenges, progress


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(title="Challenge Platform API")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - start) * 1000
    logging.getLogger("api").info(
        "%s %s -> %s (%.2fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.on_event("shutdown")
def on_shutdown() -> None:
    close_db()


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=api_response(str(exc.detail), None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=api_response("Validation error", exc.errors()),
    )


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
app.include_router(progress.router, prefix="/progress", tags=["progress"])
