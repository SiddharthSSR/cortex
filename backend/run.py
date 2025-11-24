#!/usr/bin/env python3
"""Run the Cortex backend server."""

import uvicorn
from app.config import get_settings


def main():
    """Run the server."""
    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
    )


if __name__ == "__main__":
    main()
