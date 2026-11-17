import asyncio
import os
from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI

app = FastAPI(title="Gateway Service", version="0.1.0")

SERVICES = {
    "rag": os.getenv("RAG_SERVICE_URL", "http://rag:8000"),
    "ingestion": os.getenv("INGESTION_SERVICE_URL", "http://ingestion:8000"),
    "deal-analyser": os.getenv("DEAL_ANALYSER_SERVICE_URL", "http://deal-analyser:8000"),
    "floorplans": os.getenv("FLOORPLANS_SERVICE_URL", "http://floorplans:8000")
}

TIMEOUT_SECONDS = 2.0  # seconds

async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        yield client


async def check_service(client: httpx.AsyncClient, name: str, url: str) -> tuple[str, str]:
    try:
        response = await client.get(f"{url}/health")
    except httpx.HTTPError:
        return name, "down"
    return name, "up" if response.status_code == 200 else "down"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "gateway", "version": app.version}


@app.get("/status")
async def status(client: Annotated[httpx.AsyncClient, Depends(get_http_client)]) -> dict:
    results = await asyncio.gather(
        *(check_service(client, name, url) for name, url in SERVICES.items())
    )
    services = dict(results)
    overall = "ok" if all(state == "up" for state in services.values()) else "degraded"
    return {"status": overall, "services": services}
