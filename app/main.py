from fastapi import FastAPI

app = FastAPI(title="CampusHub Club & Event Service", version="1.0.0")

@app.get("/health", tags=["Health"])
def health_check():
    return {"service": "club-event-service", "status": "UP", "version": "1.0.0"}
