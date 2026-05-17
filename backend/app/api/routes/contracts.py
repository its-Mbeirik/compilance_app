"""Contract management endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import os
import shutil
from pathlib import Path
import uuid

from app.main import get_db
from app.models.database import Contract
from app.services.document_processor import DocumentProcessor

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class ContractUploadResponse(BaseModel):
    """Response model for contract upload."""

    contract_id: str
    filename: str
    document_type: str
    status: str
    message: str


class ContractMetadata(BaseModel):
    """Contract metadata."""

    contract_id: str
    filename: str
    document_type: str  # "statuts_entreprise" or "contrat_travail"
    upload_date: str
    size_mb: float
    status: str


@router.post("/contracts/upload", response_model=ContractUploadResponse)
async def upload_contract(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a contract document for compliance verification.

    Supported formats: PDF, DOCX
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Validate file extension
    valid_extensions = {".pdf", ".docx", ".doc"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in valid_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Supported: {valid_extensions}")

    try:
        # Generate contract ID
        contract_id = str(uuid.uuid4())

        # Save file to disk
        file_path = UPLOAD_DIR / contract_id / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file.file.seek(0)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Get file size
        file_size_bytes = os.path.getsize(file_path)

        # Detect document type from filename
        filename_lower = file.filename.lower()
        if "statut" in filename_lower or "statute" in filename_lower:
            document_type = "statuts_entreprise"
        elif "contrat" in filename_lower or "travail" in filename_lower or "contract" in filename_lower:
            document_type = "contrat_travail"
        else:
            # Try to detect from content if needed
            document_type = "contrat_travail"  # Default

        # Create contract record in database
        contract = Contract(
            id=contract_id,
            filename=file.filename,
            document_type=document_type,
            file_path=str(file_path),
            file_size_bytes=file_size_bytes,
            status="uploaded",
        )
        db.add(contract)
        db.commit()
        db.refresh(contract)

        return ContractUploadResponse(
            contract_id=contract_id,
            filename=file.filename,
            document_type=document_type,
            status="uploaded",
            message="Contract uploaded successfully. Ready for compliance verification.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/contracts/{contract_id}", response_model=ContractMetadata)
async def get_contract(contract_id: str, db: Session = Depends(get_db)):
    """Retrieve contract metadata and status."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    size_mb = contract.file_size_bytes / (1024 * 1024)

    return ContractMetadata(
        contract_id=str(contract.id),
        filename=contract.filename,
        document_type=contract.document_type,
        upload_date=contract.uploaded_at.isoformat() if contract.uploaded_at else "",
        size_mb=size_mb,
        status=contract.status,
    )


@router.get("/contracts")
async def list_contracts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List uploaded contracts with pagination."""
    contracts = db.query(Contract).offset(skip).limit(limit).all()
    total = db.query(Contract).count()

    contract_list = []
    for contract in contracts:
        size_mb = contract.file_size_bytes / (1024 * 1024)
        contract_list.append({
            "contract_id": str(contract.id),
            "filename": contract.filename,
            "document_type": contract.document_type,
            "upload_date": contract.uploaded_at.isoformat() if contract.uploaded_at else "",
            "size_mb": round(size_mb, 2),
            "status": contract.status,
        })

    return {
        "contracts": contract_list,
        "total": total,
        "skip": skip,
        "limit": limit,
    }
