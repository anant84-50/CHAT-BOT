from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..database import models
from ..schemas import chat as chat_schemas
from ..services.llm_service import generate_response

router = APIRouter()

@router.post("/", response_model=chat_schemas.ChatResponse)
async def chat_endpoint(request: chat_schemas.ChatRequest, db: Session = Depends(get_db)):
    if not request.conversation_id:
        conv = models.Conversation(title=request.message[:30] + "...")
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
    else:
        conversation_id = request.conversation_id
        conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # Add user message
    user_msg = models.Message(conversation_id=conversation_id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()
    
    # Process with LLM / RAG / Search
    history = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at).all()
    history_dicts = [{"role": m.role, "content": m.content} for m in history]
    
    reply_content, sources = await generate_response(request.message, history_dicts, db, conversation_id)
    
    # Add assistant message
    import json
    sources_str = json.dumps(sources) if sources else None
    asst_msg = models.Message(
        conversation_id=conversation_id,
        role="assistant",
        content=reply_content,
        sources_json=sources_str
    )
    db.add(asst_msg)
    db.commit()
    
    return chat_schemas.ChatResponse(reply=reply_content, conversation_id=conversation_id, sources=sources)


@router.get("/conversations", response_model=List[chat_schemas.Conversation])
def get_conversations(db: Session = Depends(get_db)):
    return db.query(models.Conversation).order_by(models.Conversation.updated_at.desc()).all()

@router.get("/conversations/{conversation_id}", response_model=chat_schemas.Conversation)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return {"status": "deleted"}
