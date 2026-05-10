from json import JSONDecodeError

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from config import settings
from model import HFClient, GrammarModel

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5/minute"]
)

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.add_middleware(SlowAPIMiddleware)

client = HFClient(
    hf_access_token=settings.hf_access_token
)

model = GrammarModel(client)

# middleware
@app.middleware("http")
async def check_app_key(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    app_key = request.headers.get("X-APP-KEY")

    if app_key != settings.app_key:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Unauthorized"
            }
        )

    return await call_next(request)

# routes
@app.post("/check")
@limiter.limit("5/minute")
async def check_grammar(request: Request):

    content_type = request.headers.get(
        "content-type",
        ""
    )

    if "application/json" not in content_type:

        return JSONResponse(
            status_code=400,
            content={
                "error": (
                    "Content-Type must be application/json"
                )
            }
        )

    try:
        data = await request.json()
    except JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid JSON body"
            }
        )
    text = data.get("text")
    
    if not text:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Missing 'text' field"
            }
        )
        
    if not isinstance(text, str):
        return JSONResponse(
            status_code=400,
            content={
                "error": "'text' must be a string"
            }
        )
        
    try:
        result = model.check(text)
        return JSONResponse(
            status_code=200,
            content=result
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Inference failed",
                "details": str(e)
            }
        )