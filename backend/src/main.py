from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from src.database import init_db
from src.exceptions import TokenExpiredException, TokenNoFoundException
from src.user.router import router as users_router
from src.indicator.router import router as indicators_router
from src.function.router import router as function_router
from src.project.router import router as project_router
from src.module.router import router as module_router
from src.level.router import router as level_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="IBS", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(indicators_router)
app.include_router(function_router)
app.include_router(project_router)
app.include_router(module_router)
app.include_router(level_router)


@app.exception_handler(TokenExpiredException)
async def token_expired_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(TokenNoFoundException)
async def token_no_found_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=9000, reload=True)