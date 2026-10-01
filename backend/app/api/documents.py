from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import shutil
from typing import Optional
from ..database.database import get_db
from ..database import models
from ..services.rag_service import process_document

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    if not conversation_id:
        conv = models.Conversation(title=f"Doc: {file.filename}")
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        doc_id = process_document(file_path, file.filename, file.content_type, conversation_id, db)
        return {"status": "success", "document_id": doc_id, "conversation_id": conversation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/edit")
async def edit_document(
    document_id: int = Form(...),
    instructions: str = Form(...),
    db: Session = Depends(get_db)
):
    # Retrieve doc
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Placeholder for actual document editing logic using LLM
    # In a full implementation, the LLM would read the doc, modify it based on instructions, 
    # and save a new file.
    
    return {"status": "success", "message": "Document edited successfully (placeholder)", "download_url": f"/api/documents/download/{doc.id}"}

@router.get("/download/{document_id}")
def download_document(document_id: int, db: Session = Depends(get_db)):
    from fastapi.responses import FileResponse
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File missing from disk")
        
    return FileResponse(path=doc.file_path, filename=f"edited_{doc.filename}")

