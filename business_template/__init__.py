"""Top-level shim package to support running from the repository root.

This package re-exports the real application implementation under `src/business_template`.
"""

from src.business_template import main  # noqa: F401

__all__ = ["main"]
