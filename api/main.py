
# api/main.py
import uvicorn
from fastapi import FastAPI

# Routers
from api.routers import expenses
from api.routers import ml_routes    

# DB
from api.db.session import engine
from api.db import models

app = FastAPI(title="AI Expense Assistant - API")

# Include routers
app.include_router(expenses.router)
app.include_router(ml_routes.router)   # <-- ADD THIS LINE


@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=engine)

@app.get("/", tags=["root"])
def root():
    return {"status": "ok", "service": "ai_expense_assistant.api"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
