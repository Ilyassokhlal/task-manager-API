from fastapi import APIRouter, Depends, Request

from app.models.user import User
from app.schemas.user import UserResponse
from app.utils.security import get_current_user
from app.utils.limiter import limiter

router = APIRouter(prefix="/users", tags= ["Users"])

@router.get("/me", response_model=UserResponse,
    responses={
        401: {"description": "Not authenticated"},
    },
    summary="Get the current user's profile"
)
@limiter.limit("60/minute")
def get_my_profile(request: Request, current_user: User = Depends(get_current_user)):
    """
    Get the current user's profile.

    - This endpoint returns the profile information of the currently authenticated user.
    - Requires a valid JWT access token in the Authorization header.
    - Returns a 401 error if the user is not authenticated.
    """
    return current_user