"""CLI entry point."""

import uvicorn

from novelvids.core.config import settings


def main() -> None:
    """Run the application server."""
    uvicorn.run(
        "novelvids.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
