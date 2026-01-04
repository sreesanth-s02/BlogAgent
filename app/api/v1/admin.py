from fastapi import APIRouter, Depends
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/admin/blogger/status")
def blogger_status(user=Depends(get_current_user)):
    """
    Check whether Blogger OAuth is completed for current user
    """
    return {
        "connected": bool(user.get("blogger_token"))
    }
