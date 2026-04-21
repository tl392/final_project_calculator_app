from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta, date, time
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import Base, get_db, engine
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import CalculationBase, CalculationResponse, CalculationUpdate
from app.schemas.report import ReportSummaryResponse
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserResponse, UserLogin


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Calculations API",
    description="API for managing calculations",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse, tags=["web"])
def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/login", response_class=HTMLResponse, tags=["web"])
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})


@app.get("/register", response_class=HTMLResponse, tags=["web"])
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={})


@app.get("/dashboard", response_class=HTMLResponse, tags=["web"])
def dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={})


@app.get("/reports", response_class=HTMLResponse, tags=["web"])
def reports_page(request: Request):
    return templates.TemplateResponse(request=request, name="reports.html", context={"request": request})


@app.get("/dashboard/view/{calc_id}", response_class=HTMLResponse, tags=["web"])
def view_calculation_page(request: Request, calc_id: str):
    return templates.TemplateResponse(request=request, name="view_calculation.html", context={"request": request, "calc_id": calc_id})


@app.get("/dashboard/edit/{calc_id}", response_class=HTMLResponse, tags=["web"])
def edit_calculation_page(request: Request, calc_id: str):
    return templates.TemplateResponse(request=request, name="edit_calculation.html", context={"request": request, "calc_id": calc_id})


@app.get("/health", tags=["health"])
def read_health():
    return {"status": "ok"}


@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    user_data = user_create.dict(exclude={"confirm_password"})
    try:
        user = User.register(db, user_data)
        db.commit()
        db.refresh(user)
        return user
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login_json(user_login: UserLogin, db: Session = Depends(get_db)):
    auth_result = User.authenticate(db, user_login.username, user_login.password)
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_result["user"]
    db.commit()
    expires_at = auth_result.get("expires_at")
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    return TokenResponse(
        access_token=auth_result["access_token"],
        refresh_token=auth_result["refresh_token"],
        token_type="bearer",
        expires_at=expires_at,
        user_id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )


@app.post("/auth/token", tags=["auth"])
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    auth_result = User.authenticate(db, form_data.username, form_data.password)
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": auth_result["access_token"], "token_type": "bearer"}


@app.post("/calculations", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED, tags=["calculations"])
def create_calculation(calculation_data: CalculationBase, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    try:
        new_calculation = Calculation.create(
            calculation_type=calculation_data.type,
            user_id=current_user.id,
            inputs=calculation_data.inputs,
        )
        new_calculation.result = new_calculation.get_result()
        db.add(new_calculation)
        db.commit()
        db.refresh(new_calculation)
        return new_calculation
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/calculations", response_model=List[CalculationResponse], tags=["calculations"])
def list_calculations(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(Calculation).filter(Calculation.user_id == current_user.id).order_by(Calculation.created_at.desc()).all()


@app.get("/calculations/{calc_id}", response_model=CalculationResponse, tags=["calculations"])
def get_calculation(calc_id: str, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")

    calculation = db.query(Calculation).filter(Calculation.id == calc_uuid, Calculation.user_id == current_user.id).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")
    return calculation


@app.put("/calculations/{calc_id}", response_model=CalculationResponse, tags=["calculations"])
def update_calculation(calc_id: str, calculation_update: CalculationUpdate, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")

    calculation = db.query(Calculation).filter(Calculation.id == calc_uuid, Calculation.user_id == current_user.id).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")

    if calculation_update.inputs is not None:
        calculation.inputs = calculation_update.inputs
        try:
            calculation.result = calculation.get_result()
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    calculation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(calculation)
    return calculation


@app.delete("/calculations/{calc_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["calculations"])
def delete_calculation(calc_id: str, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")

    calculation = db.query(Calculation).filter(Calculation.id == calc_uuid, Calculation.user_id == current_user.id).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")

    db.delete(calculation)
    db.commit()
    return None


@app.get("/reports/summary", response_model=ReportSummaryResponse, tags=["reports"])
def report_summary(
    calculation_type: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(Calculation).filter(Calculation.user_id == current_user.id)

    if calculation_type:
        query = query.filter(Calculation.type == calculation_type.lower())
    if start_date:
        query = query.filter(Calculation.created_at >= datetime.combine(start_date, time.min))
    if end_date:
        query = query.filter(Calculation.created_at <= datetime.combine(end_date, time.max))

    calculations = query.order_by(Calculation.created_at.desc()).all()
    all_types = [
        "addition",
        "subtraction",
        "multiplication",
        "division",
        "exponentiation",
        "modulus",
        "sqrt",
    ]
    count_by_type = {calc_type: 0 for calc_type in all_types}
    operand_values = []
    operand_counts = []
    preview_items = []

    for calc in calculations:
        count_by_type[calc.type] = count_by_type.get(calc.type, 0) + 1
        operand_values.extend(calc.inputs or [])
        operand_counts.append(len(calc.inputs or []))
        preview_items.append(
            {
                "id": calc.id,
                "type": calc.type,
                "inputs": calc.inputs,
                "result": calc.result,
                "created_at": calc.created_at.isoformat(),
            }
        )

    average_of_operands = round(sum(operand_values) / len(operand_values), 4) if operand_values else 0.0
    average_operands_per_calculation = round(sum(operand_counts) / len(operand_counts), 4) if operand_counts else 0.0

    return {
        "filters": {
            "calculation_type": calculation_type.lower() if calculation_type else None,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": f"{current_user.first_name} {current_user.last_name}",
        },
        "total_calculations": len(calculations),
        "count_by_type": count_by_type,
        "average_of_operands": average_of_operands,
        "average_operands_per_calculation": average_operands_per_calculation,
        "calculations": preview_items,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, log_level="info")
