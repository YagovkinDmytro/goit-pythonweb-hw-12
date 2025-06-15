from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User, RequestEmail
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.services.email import send_email
from src.database.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, 
    background_tasks: BackgroundTasks, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Handles user registration by checking for existing users with the same email or username, 
    hashing the provided password, creating a new user, and sending a confirmation email.
    Args:
        user_data (UserCreate): The user data to be registered.
        background_tasks (BackgroundTasks): The background tasks to be executed.
        request (Request): The current request.
        db (Session, optional): The database session. Defaults to Depends(get_db).
    Returns:
        User: The newly registered user.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_user_email(user_data.user_email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with such email already exists",
        )

    username_user = await user_service.get_user_by_user_name(user_data.user_name)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this name already exists",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.user_email, new_user.user_name, request.base_url
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Handles user login by verifying the provided username and password, 
    and returning an access token if the credentials are valid.
    Args:
        form_data (OAuth2PasswordRequestForm): The user's login credentials.
        db (Session): The database session.
    Returns:
        Token: The access token for the authenticated user.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_user_name(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email address not confirmed",
        )

    access_token = await create_access_token(data={"sub": user.user_name})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Handles email confirmation by verifying the provided token, 
    checking the user's confirmation status, and updating the status if necessary.
    
    Args:
        token (str): The email confirmation token.
        db (Session): The database session.
    
    Returns:
        dict: A message indicating whether the email has been confirmed or not.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_user_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email has already been confirmed."}
    await user_service.confirmed_user_email(email)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handles email re-confirmation by checking the user's confirmation status and 
    sending a confirmation email if necessary.
    Args:
        body (RequestEmail): The user's email address to be re-confirmed.
        background_tasks (BackgroundTasks): The background tasks to be executed.
        request (Request): The current request.
        db (Session, optional): The database session. Defaults to Depends(get_db).
    Returns:
        dict: A message indicating whether the email has been confirmed or not.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_user_email(body.user_email)

    if user.confirmed:
        return {"message": "Your email has already been confirmed."}
    if user:
        background_tasks.add_task(
            send_email, user.user_email, user.user_name, request.base_url
        )
    return {"message": "Check your email for confirmation."}
