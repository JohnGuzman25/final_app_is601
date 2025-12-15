from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.auth.security import decode_token

router = APIRouter(prefix="/transactions", tags=["transactions"])
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


@router.get("", response_class=HTMLResponse)
def list_transactions(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .all()
    )
    return templates.TemplateResponse("transactions.html", {"request": request, "user": user, "txs": txs, "error": None})


@router.post("/add")
def add_transaction(
    request: Request,
    tx_type: str = Form(...),
    category: str = Form(...),
    note: str = Form(""),
    amount: float = Form(...),
    db: Session = Depends(get_db),
):
    user = get_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if tx_type not in ("income", "expense"):
        return templates.TemplateResponse("transactions.html", {"request": request, "user": user, "txs": [], "error": "Bad type"})

    tx = Transaction(user_id=user.id, tx_type=tx_type, category=category, note=note, amount=amount)
    db.add(tx)
    db.commit()
    return RedirectResponse(url="/transactions", status_code=303)
