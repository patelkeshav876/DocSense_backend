from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, documents, chat
import logging

logging.basicConfig(level=logging.INFO)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DocuSense AI API", version="1.0.0")

# CORS middleware - add BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers AFTER middleware
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
def read_root():
    return {"message": "DocuSense AI API"}