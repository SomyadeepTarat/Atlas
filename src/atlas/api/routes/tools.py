from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from atlas.schemas.model import (
    ToolExecuteRequest,
)
from atlas.tools.dependencies import (
    get_tool_executor,
)
from atlas.tools.errors import (
    ToolApprovalRequiredError,
    ToolError,
    ToolExecutionUnknownError,
    ToolNotFoundError,
    ToolPermissionDeniedError,
)
from atlas.tools.executor import (
    ToolExecutor,
)
from atlas.tools.types import (
    ToolExecutionContext,
    ToolPermission,
)

router = APIRouter(
    prefix="/tools",
    tags=["tools"],
)


@router.post("/execute")
async def execute_tool(
    payload: ToolExecuteRequest,
    executor: ToolExecutor = Depends(get_tool_executor),
):
    try:
        permissions = frozenset(ToolPermission(item) for item in payload.permissions)

        result = await executor.execute(
            tool_name=payload.tool_name,
            raw_input=payload.arguments,
            context=ToolExecutionContext(
                permissions=permissions,
                approved_tools=frozenset(payload.approved_tools),
            ),
        )

        return {
            "output": result.output.model_dump(),
            "outcome": result.outcome.value,
            "meta": {
                "tool_name": (result.metadata.tool_name),
                "attempts": (result.metadata.attempts),
                "duration_seconds": (result.metadata.duration_seconds),
            },
        }

    except ToolNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ToolPermissionDeniedError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc

    except ToolApprovalRequiredError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except ToolExecutionUnknownError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except (
        ValueError,
        ToolError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
