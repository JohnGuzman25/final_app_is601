from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.auth.security import decode_token

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="templates")


def get_user_from_cookie(request: Request, db: Session) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            return None
    except Exception:
        return None
    return db.query(User).filter(User.username == username).first()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    total_income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.user_id == user.id, Transaction.tx_type == "income")
        .scalar()
    )
    total_expense = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.user_id == user.id, Transaction.tx_type == "expense")
        .scalar()
    )

    recent = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "net": float(total_income) - float(total_expense),
            "recent": recent,
        },
    )
