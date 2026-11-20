from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.routers import club_router, event_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CampusHub Club & Event Service", version="1.0.0")


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP_ERROR", "message": str(exc.detail)}
    )


@app.get("/health", tags=["Health"])
def health_check():
    return {"service": "club-event-service", "status": "UP", "version": "1.0.0"}


app.include_router(club_router.router)
app.include_router(event_router.router)