import sys
import os

# Inject backend path into sys natively without hacking FastAPI routing tables
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_path)

from app.main import app
