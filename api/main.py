# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "Hello from FastAPI Backend!"}

# api/main.py
import uvicorn
from fastapi import FastAPI
from api.routers import expenses
from api.db.session import engine
from api.db import models

app = FastAPI(title="AI Expense Assistant - API (Phase 1)")

# Include routers
app.include_router(expenses.router)

@app.on_event("startup")
def startup():
    # Ensure tables exist - simple migration bootstrap
    models.Base.metadata.create_all(bind=engine)

@app.get("/", tags=["root"])
def root():
    return {"status": "ok", "service": "ai_expense_assistant.api"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
