import sys
import os
import traceback

backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_path)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Satisfy Vercel AST static parser limitation at build time
app = FastAPI()

try:
    from app.main import app as backend_app
    # Satisfy ASGI dynamic runtime by re-binding the object after AST parsing
    app = backend_app
except Exception as e:
    # If the boot fails (e.g. Pandas Lambda C-Extension crash), trap the stack trace
    err_str = f"VERCEL BOOT TRAP: {str(e)} | TRACE: {traceback.format_exc()}"
    print(err_str)
    
    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def catch_all(request: Request, path_name: str):
        return JSONResponse(status_code=500, content={"detail": err_str})
