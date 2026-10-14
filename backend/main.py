import logging
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from backend.services.agent_router import route_query
from backend.config import settings
from backend.services.finance_service import (
    get_transactions,
    get_expenses,
    get_revenue,
    get_summary,
    get_invoices,
    get_receivables,
    get_vendor_expenses
)
from backend.services.finance_agent import run_finance_agent
from pydantic import BaseModel, Field, field_validator
from fastapi.middleware.cors import CORSMiddleware



class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty or whitespace.")
        return value

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered financial assistant",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request, exc):
    logger.error(
    "Database error while handling request %s: %s",
    request.url.path,
    exc,
    )
    return JSONResponse(
        status_code=503,
        content={
            "detail": "The database is temporarily unavailable. Please try again later."
        },
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }


@app.get("/transactions")
def transactions():
    return get_transactions()


@app.get("/expenses")
def expenses():
    return get_expenses()


@app.get("/revenue")
def revenue():
    return get_revenue()


@app.get("/summary")
def summary():
    return get_summary()


@app.get("/invoices")
def invoices():
    return get_invoices()


@app.get("/receivables")
def receivables():
    return get_receivables()


@app.get("/vendors/{vendor}")
def vendor_expenses(vendor: str):
    return get_vendor_expenses(vendor)





@app.post("/chat")
def chat(request: ChatRequest):
    try:
        return {"response": route_query(request.message)}
    except Exception:
        logger.exception("Unexpected error while processing chat request")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your message.",
        )