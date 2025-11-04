from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.exceptions import TokenExpiredException, TokenNoFoundException
from src.user.router import router as users_router
from src.indicator.router import router as indicators_router
from src.function.router import router as function_router
from src.project.router import router as project_router

app = FastAPI(title='IBS')
PORT = 9000
HOST = "0.0.0.0"

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


@app.exception_handler(TokenExpiredException)
async def token_expired_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(TokenNoFoundException)
async def token_no_found_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    uvicorn.run('src.main:app', host = HOST, port=PORT, reload = True)