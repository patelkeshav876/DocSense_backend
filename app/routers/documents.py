from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.routers.auth import get_current_user
from app.services.document_service import DocumentService

router = APIRouter()
doc_service = DocumentService()

@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if file.content_type not in ["text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    content = await file.read()
    document = await doc_service.process_document(file.filename, file.content_type, len(content), content, current_user.id, db)
    return document

@router.get("/", response_model=List[schemas.Document])
def get_documents(
    skip: int = 0, limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    documents = db.query(models.Document).filter(models.Document.user_id == current_user.id).offset(skip).limit(limit).all()
    return documents

@router.get("/{doc_id}", response_model=schemas.Document)
def get_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    document = db.query(models.Document).filter(models.Document.id == doc_id, models.Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document