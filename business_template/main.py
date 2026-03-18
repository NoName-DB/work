"""Shim entrypoint so `uvicorn business_template.main:app` works from the repo root."""

from src.business_template.main import app  # noqa: F401
