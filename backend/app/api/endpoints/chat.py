from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import rag_service
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ChatHistory



router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Multilingual Chat Endpoint with History Logging.
    """
    try:
        # Generate response
        response_data = await rag_service.generate_response(request)
        
        # Save Interaction to Database
        try:
            db_log = ChatHistory(
                query=request.query,
                response=response_data.response
            )
            db.add(db_log)
            db.commit()
        except Exception as db_err:
            print(f"Database Error: {db_err}")
            # Continue even if logging fails
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
