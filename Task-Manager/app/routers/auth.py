from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.schemas.user import RegisterRequest, LoginRequest, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.notifications import send_notification, log_activity

from app.utils.limiter import limiter


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED,
    responses={
        422: {"description": "Validation Error"},
        409: {"description": "Email or Username already registered"},
        429: {"description": "Too many requests"},
    },
    summary="Create a new user account and return an access token",
)
@limiter.limit("20/minute")
def register(request: Request, payload: RegisterRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Create a new user account and return an access token.

    - The password is hashed before storing in the database.
    - Returns a JWT access token upon successful registration.
    """

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Email or Username already registered"
        )
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})

    background_tasks.add_task(send_notification, email=payload.email, message=f"Hi {payload.username}, thank you for registering using my API!")
    print(f"Background task added | Send a welcome email to {payload.email}")
    background_tasks.add_task(log_activity, user_id=user.id, action="User registered")
    print(f"Background task added | Log activity for user_id {user.id}")

    return{
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=TokenResponse, description="Login using email instead of username",
    responses={
        422: {"description": "Validation Error"},
        401: {"description": "Invalid email or password"},
        429: {"description": "Too many requests"},
    },
    summary="Login using email and password and return an access token",
)
@limiter.limit("5/minute")
def login(request: Request,credentials: LoginRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Login using email and password and return an access token.

    - This endpoint authenticates the user and returns a JWT access token upon successful login.
    -Raises a 401 error if the email or password is invalid.
    """

    # No email sent upon login, but we will log the activity in the background

    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = create_access_token(data={"sub": str(user.id)})

    background_tasks.add_task(log_activity, user_id=user.id, action="User logged in")
    print(f"Background task added | Log activity for user_id {user.id}")

    return {
        "access_token": token,
        "token_type": "bearer"
    }
