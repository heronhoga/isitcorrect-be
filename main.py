from fastapi import FastAPI, Request
from config import settings
from starlette.responses import JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# rate limit
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5/minute"]
)

app = FastAPI()
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def check_app_key(request: Request, call_next):
    app_key = request.headers.get("X-APP-KEY")
    if app_key != settings.app_key:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    return await call_next(request)

@app.get("/")
async def read_root(request: Request):
    return {"Hello": "World"}

@app.get("/items/{item_id}")
@limiter.limit("10/minute")
async def read_item(request: Request, item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}