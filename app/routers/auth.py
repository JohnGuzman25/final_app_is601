from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.token import TokenResponse
from app.auth.security import hash_password, verify_password, create_access_token, create_email_verify_token, decode_token
from app.auth.email import send_verification_email
from app.core_config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

# create tables (simple + fast)


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@router.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if db.query(User).filter((User.email == email) | (User.username == username)).first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email or username already used"})

    user = User(email=email, username=username, hashed_password=hash_password(password), is_verified=False)
    db.add(user)
    db.commit()

    token = create_email_verify_token(username)
    verify_url = f"{settings.APP_BASE_URL}/auth/verify?token={token}"
    send_verification_email(email, verify_url)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Account created. Check server logs for verification link (demo)."},
    )


@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
        if payload.get("purpose") != "email_verify":
            raise ValueError("bad purpose")
        username = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.commit()
    return RedirectResponse(url="/auth/login", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_model=TokenResponse)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    token = create_access_token(username)
    return TokenResponse(access_token=token)


@router.post("/login-ui")
def login_ui(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # UI helper: login and store token in cookie
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": {"method": "GET"}, "error": "Invalid credentials"})
    if not user.is_verified:
        return templates.TemplateResponse("login.html", {"request": {"method": "GET"}, "error": "Verify email first (use link in server logs)"})

    token = create_access_token(username)
    resp = RedirectResponse(url="/dashboard", status_code=303)
    resp.set_cookie("access_token", token, httponly=True, samesite="lax")
    return resp


@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/auth/login", status_code=303)
    resp.delete_cookie("access_token")
    return resp
