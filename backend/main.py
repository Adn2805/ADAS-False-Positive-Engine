# Thin ASGI entrypoint for Vercel Serverless Function deployment
import sys
import traceback

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def catch_all(path_name: str):
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Vercel Import Crash: {str(e)} | TRACE: {traceback.format_exc()}"}
        )
