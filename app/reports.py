from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.calculation import Calculation
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def reports_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Total calculations in the system
    total_calcs = db.query(func.count(Calculation.id)).scalar() or 0

    # Total calculations for the logged-in user
    my_calcs = (
        db.query(func.count(Calculation.id))
        .filter(Calculation.user_id == current_user.id)
        .scalar()
        or 0
    )

    # Most recent calc timestamp (system-wide)
    latest_calc_at = db.query(func.max(Calculation.created_at)).scalar()

    return templates.TemplateResponse(
        "reports.html",
        {
            "request": request,
            "user": current_user,
            "total_calcs": total_calcs,
            "my_calcs": my_calcs,
            "latest_calc_at": latest_calc_at,
        },
    )

