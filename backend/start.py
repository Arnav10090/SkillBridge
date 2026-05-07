import os

import uvicorn


def get_port() -> int:
    raw_port = os.getenv("PORT", "8000")
    try:
        return int(raw_port)
    except ValueError:
        print(f"Invalid PORT={raw_port!r}; falling back to 8000")
        return 8000


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = get_port()
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    print(f"Starting SkillBridge API on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, log_level=log_level)
