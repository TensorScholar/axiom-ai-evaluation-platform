from fastapi import FastAPI

from app.config import HEALTH_STATUS, SERVICE_NAME

app = FastAPI(title="AXIOM")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": HEALTH_STATUS, "service": SERVICE_NAME}
