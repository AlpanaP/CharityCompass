from fastapi import FastAPI

app = FastAPI(title="Charity Compass API")


@app.get("/health")
def read_health() -> dict[str, str]:
    """Simple health check endpoint used for monitoring."""
    return {"status": "ok"}
