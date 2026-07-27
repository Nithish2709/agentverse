"""ASGI entry point — used by uvicorn."""

from app.main import create_app

app = create_app()
