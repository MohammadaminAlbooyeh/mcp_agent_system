from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from agent.core.session_manager import SessionManager
from backend.services.session_repository import SessionRepository
from backend.api.dependencies import get_session_manager
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = None
    metadata: Optional[dict] = None


class SessionResponse(BaseModel):
    id: str
    user_id: Optional[str]
    state: dict
    memory_snapshot: dict
    created_at: str
    updated_at: str
    expires_at: str
    is_active: bool
    status: str
    metadata: dict
    step_count: int


class SessionStatusRequest(BaseModel):
    status: str


class SessionStateRequest(BaseModel):
    state_updates: dict


@router.post("/create", response_model=SessionResponse)
async def create_session(
    request: SessionCreateRequest,
    session_manager: SessionManager = Depends(get_session_manager),
) -> SessionResponse:
    try:
        session_id = await session_manager.create_session(
            user_id=request.user_id,
            metadata=request.metadata
        )
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=500, detail="Failed to create session")

        return SessionResponse(
            id=session["id"],
            user_id=session["user_id"],
            state=session["state"],
            memory_snapshot=session["memory_snapshot"],
            created_at=session["created_at"].isoformat() if isinstance(session["created_at"], datetime) else str(session["created_at"]),
            updated_at=session["updated_at"].isoformat() if isinstance(session["updated_at"], datetime) else str(session["updated_at"]),
            expires_at=session["expires_at"].isoformat() if isinstance(session["expires_at"], datetime) else str(session["expires_at"]),
            is_active=session["is_active"],
            status=session["status"],
            metadata=session["metadata"],
            step_count=session.get("step_count", 0),
        )
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager),
) -> SessionResponse:
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionResponse(
            id=session["id"],
            user_id=session["user_id"],
            state=session["state"],
            memory_snapshot=session["memory_snapshot"],
            created_at=session["created_at"].isoformat() if isinstance(session["created_at"], datetime) else str(session["created_at"]),
            updated_at=session["updated_at"].isoformat() if isinstance(session["updated_at"], datetime) else str(session["updated_at"]),
            expires_at=session["expires_at"].isoformat() if isinstance(session["expires_at"], datetime) else str(session["expires_at"]),
            is_active=session["is_active"],
            status=session["status"],
            metadata=session["metadata"],
            step_count=session.get("step_count", 0),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/state", response_model=dict)
async def update_session_state(
    session_id: str,
    request: SessionStateRequest,
    session_manager: SessionManager = Depends(get_session_manager),
) -> dict:
    try:
        success = await session_manager.update_session_state(session_id, request.state_updates)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "message": "Session state updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update session state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/pause", response_model=dict)
async def pause_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager),
) -> dict:
    try:
        success = await session_manager.pause_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "message": "Session paused"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pause session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/resume", response_model=dict)
async def resume_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager),
) -> dict:
    try:
        success = await session_manager.resume_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "message": "Session resumed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/complete", response_model=dict)
async def complete_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager),
) -> dict:
    try:
        success = await session_manager.complete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "message": "Session completed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}", response_model=dict)
async def delete_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager),
) -> dict:
    try:
        success = await session_manager.cleanup_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "message": "Session deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[SessionResponse])
async def list_active_sessions(
    user_id: Optional[str] = None,
    limit: int = 100,
    session_manager: SessionManager = Depends(get_session_manager),
) -> List[SessionResponse]:
    try:
        sessions = await session_manager.list_active_sessions(user_id=user_id, limit=limit)
        result = []
        for session in sessions:
            result.append(SessionResponse(
                id=session["id"],
                user_id=session["user_id"],
                state=session["state"],
                memory_snapshot=session["memory_snapshot"],
                created_at=session["created_at"].isoformat() if isinstance(session["created_at"], datetime) else str(session["created_at"]),
                updated_at=session["updated_at"].isoformat() if isinstance(session["updated_at"], datetime) else str(session["updated_at"]),
                expires_at=session["expires_at"].isoformat() if isinstance(session["expires_at"], datetime) else str(session["expires_at"]),
                is_active=session["is_active"],
                status=session["status"],
                metadata=session["metadata"],
                step_count=session.get("step_count", 0),
            ))
        return result
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup-expired", response_model=dict)
async def cleanup_expired_sessions(
    session_manager: SessionManager = Depends(get_session_manager),
) -> dict:
    try:
        count = await session_manager.cleanup_expired_sessions()
        return {
            "success": True,
            "message": f"Cleaned up {count} expired sessions",
            "count": count
        }
    except Exception as e:
        logger.error(f"Failed to cleanup expired sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
