from fastapi import FastAPI

app = FastAPI(title= "gateway", version= "0.1.0", description= "This is the gateway service for the property-rag project")


@app.get("/health")
def health() -> dict[str,str]:
    """Liveness check, is the gateway process up?"""
    return {"status": "ok", "service": "gateway"}