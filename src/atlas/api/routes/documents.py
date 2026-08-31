from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from atlas.retrieval.dependencies import (
    get_retrieval_service,
)
from atlas.retrieval.service import (
    RetrievalService,
)
from atlas.schemas.retrieval import (
    DocumentIngestResponse,
)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post(
    "/upload",
    response_model=DocumentIngestResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    retrieval: RetrievalService = Depends(get_retrieval_service),
) -> DocumentIngestResponse:
    filename = file.filename or "document.pdf"

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE),
            detail=("Only PDF files are supported in this milestone."),
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    temp_path: Path | None = None

    try:
        with NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp:
            temp.write(content)

            temp_path = Path(temp.name)

        document_id, chunk_count = retrieval.ingest_pdf(
            temp_path,
            filename=filename,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

    return DocumentIngestResponse(
        document_id=document_id,
        filename=filename,
        chunks_created=chunk_count,
    )
