from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import pandas as pd
import io
from typing import Dict, Any

from db.session import get_db

router = APIRouter()

class UploadResponse(BaseModel):
    success: bool
    message: str
    data_preview: Dict[str, Any]
    rows_count: int

@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Read file content
        content = await file.read()
        
        # Parse CSV with pandas
        try:
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")
        
        # Basic validation
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # TODO: Store relevant data in database
        # For now, we'll just analyze and return preview
        
        # Get basic info about the data
        data_preview = {
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "sample_rows": df.head(5).to_dict(orient='records'),
            "summary_stats": df.describe().to_dict() if df.select_dtypes(include='number').shape[1] > 0 else {}
        }
        
        return UploadResponse(
            success=True,
            message=f"Successfully uploaded and parsed {file.filename}",
            data_preview=data_preview,
            rows_count=len(df)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/upload/status")
async def upload_status():
    # TODO: Return status of uploaded files
    return {"message": "Upload status endpoint - TODO: implement file tracking"}