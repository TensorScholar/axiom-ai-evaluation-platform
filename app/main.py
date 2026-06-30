from fastapi import FastAPI

from app.api import router as api_router
from app.config import HEALTH_STATUS, SERVICE_NAME

app = FastAPI(title="AXIOM")
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": HEALTH_STATUS, "service": SERVICE_NAME}
