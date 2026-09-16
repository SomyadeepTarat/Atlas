from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from atlas.core.config import get_settings
from atlas.retrieval.dependencies import (
    get_retrieval_service,
)
from atlas.retrieval.service import (
    RetrievalService,
)
from atlas.schemas.retrieval import (
    DocumentIngestResponse,
)
from atlas.security.errors import (
    InvalidFileError,
    ResourceLimitError,
)
from atlas.security.validation import (
    safe_display_filename,
    validate_pdf_upload,
)

settings = get_settings()

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
    filename = safe_display_filename(file.filename or "document.pdf")

    content = await file.read()

    try:
        validate_pdf_upload(
            filename=filename,
            content=content,
            max_bytes=settings.max_pdf_bytes,
            max_filename_chars=settings.max_filename_chars,
        )

    except InvalidFileError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except ResourceLimitError as exc:
        raise HTTPException(
            status_code=413,
            detail=str(exc),
        ) from exc

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
