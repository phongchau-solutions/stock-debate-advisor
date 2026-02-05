import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.crud.debate import debate_crud
from app.models.debate import DebateStatus
from app.schemas.debate import DebateCreate, DebateListResponse, DebateResponse

router = APIRouter(prefix="/debates", tags=["debates"])


@router.post("", response_model=DebateResponse, status_code=status.HTTP_201_CREATED)
async def create_debate(
    debate_data: DebateCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new debate."""

    debate_dict = debate_data.model_dump()
    debate_dict["id"] = f"debate_{uuid.uuid4().hex[:12]}"
    debate_dict["user_id"] = user_id
    debate_dict["status"] = DebateStatus.PENDING

    debate = await debate_crud.create(db, debate_dict)

    # TODO: Trigger debate orchestration in background

    return debate


@router.get("/{debate_id}", response_model=DebateResponse)
async def get_debate(
    debate_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get a specific debate."""

    debate = await debate_crud.get(db, id=debate_id)

    if not debate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debate not found")

    if debate.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this debate"
        )

    return debate


@router.get("", response_model=DebateListResponse)
async def list_debates(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    skip: int = 0,
    limit: int = 20,
):
    """List user's debates."""

    result = await debate_crud.get_multi(
        db,
        offset=skip,
        limit=limit,
        user_id=user_id,
        order_by=["created_at"],
        order_by_desc=True,
    )

    return DebateListResponse(debates=result["data"], total=result["total_count"])
