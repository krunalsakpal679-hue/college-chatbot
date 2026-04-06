from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.ingestion_service import ingestion_service

router = APIRouter()

@router.post("/")
async def ingest_data(background_tasks: BackgroundTasks):
    """
    Triggers the document ingestion process in the background.
    """
    try:
        # Run in background to avoid timeout
        background_tasks.add_task(ingestion_service.ingest_documents)
        return {"status": "accepted", "message": "Ingestion started in background. Check server logs for progress."}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
