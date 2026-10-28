from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, ApplicationStatus
from app.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    FunnelSummary,
)

router = APIRouter()


@router.post(
    "/candidaturas",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    payload: ApplicationCreate, db: Session = Depends(get_db)
) -> Application:
    application = Application(**payload.model_dump(exclude={"data_candidatura"}))
    if payload.data_candidatura is not None:
        application.data_candidatura = payload.data_candidatura
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/candidaturas", response_model=list[ApplicationResponse])
def list_applications(
    response: Response,
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    empresa: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Application]:
    query = select(Application)
    filters = []
    if status_filter is not None:
        filters.append(Application.status == status_filter)
    if empresa is not None:
        empresa = empresa.strip()
        if not empresa:
            raise HTTPException(
                status_code=422, detail="O filtro empresa não pode ficar vazio."
            )
        filters.append(Application.empresa.ilike(f"%{empresa}%"))
    if filters:
        query = query.where(*filters)
    total = db.scalar(select(func.count()).select_from(Application).where(*filters))
    response.headers["X-Total-Count"] = str(total or 0)
    query = query.order_by(Application.criado_em.desc(), Application.id.desc())
    return list(db.scalars(query.offset(offset).limit(limit)).all())


@router.get("/candidaturas/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)) -> Application:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Candidatura não encontrada.")
    return application


@router.patch("/candidaturas/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
) -> Application:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Candidatura não encontrada.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    application.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(application)
    return application


@router.delete(
    "/candidaturas/{application_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_application(application_id: int, db: Session = Depends(get_db)) -> Response:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Candidatura não encontrada.")
    db.delete(application)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/resumo", response_model=FunnelSummary)
def get_funnel_summary(db: Session = Depends(get_db)) -> FunnelSummary:
    counts = dict(
        db.execute(
            select(Application.status, func.count(Application.id)).group_by(
                Application.status
            )
        ).all()
    )
    by_status = {item: counts.get(item, 0) for item in ApplicationStatus}
    return FunnelSummary(total=sum(by_status.values()), por_status=by_status)
