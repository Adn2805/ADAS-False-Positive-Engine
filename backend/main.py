import sys
import os
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Force Vercel's AWS Lambda to recognize the 'backend' folder as the Python root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Vercel's static AST parser REQUIRES exactly "app = FastAPI()" at the top level
app = FastAPI()

try:
    from app.main import app as real_app
    # If import succeeds, merge all routes safely
    app.router.routes = real_app.router.routes
except Exception as e:
    # If Pandas/Numpy crash on Amazon Linux, we catch it here manually
    err_str = f"Vercel Boot Crash: {str(e)} | TRACE: {traceback.format_exc()}"
    print(err_str)
    
    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def catch_all(request: Request, path_name: str):
        return JSONResponse(status_code=500, content={"detail": err_str})
