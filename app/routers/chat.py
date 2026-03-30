from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.routers.auth import get_current_user
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

@router.post("/{doc_id}/ask")
async def ask_question(
    doc_id: str,
    request: schemas.AskRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if document exists and belongs to user
    document = db.query(models.Document).filter(models.Document.id == doc_id, models.Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        response = await chat_service.ask_question(doc_id, request.question, current_user.id, db)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"response": response}

@router.get("/{doc_id}/history", response_model=List[schemas.ChatMessage])
def get_chat_history(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if document exists and belongs to user
    document = db.query(models.Document).filter(models.Document.id == doc_id, models.Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    messages = db.query(models.ChatMessage).filter(models.ChatMessage.document_id == doc_id).order_by(models.ChatMessage.created_at).all()
    return messages
