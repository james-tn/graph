from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.graphrag_service import graphrag_service
from typing import List, Optional

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_path = await graphrag_service.save_file(content, file.filename)
        return {"message": f"File {file.filename} uploaded successfully", "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index")
async def run_index():
    try:
        await graphrag_service.run_ingestion()
        return {"message": "Ingestion completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    try:
        result = await graphrag_service.query(request.query)
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
