from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import ExportPDFRequest
from app.services.export_service import generate_csv, generate_pdf, generate_case_detail_pdf
import uuid
import io

router = APIRouter()


@router.post("/pdf")
async def export_pdf(
    request: ExportPDFRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case_ids_str = [str(cid) for cid in request.case_ids] if request.case_ids else None
    pdf_bytes = generate_pdf(
        session_id=request.session_id,
        case_ids=case_ids_str,
        include_charts=request.include_charts,
    )
    download_id = str(uuid.uuid4())
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=sentinelai-report-{request.session_id[:8]}.pdf",
            "Content-Length": str(len(pdf_bytes)),
            "X-Download-Id": download_id,
        },
    )


@router.post("/pdf/case/{case_id}")
async def export_case_pdf(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pdf_bytes = generate_case_detail_pdf(case_id)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=case-{case_id[:8]}.pdf",
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.post("/csv/{resource_type}")
async def export_csv(
    resource_type: str,
    resource_ids: list[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if resource_ids is None:
        resource_ids = []
    csv_bytes = generate_csv(resource_type, resource_ids)
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=sentinelai-{resource_type}.csv",
            "Content-Length": str(len(csv_bytes)),
        },
    )
