from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix='/api/v1', dependencies=[Depends(APIKeyHeader(name='X-API-Key', auto_error=False))])
Identifier = Annotated[int, Path(ge=1)]


class ApplicationCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    borrower_id: int = Field(ge=1)
    amount_usd: int = Field(ge=100, le=5000)
    term_months: Literal[3, 6, 12, 18, 24]


class Application(ApplicationCreate):
    id: int
    status: Literal['pending', 'approved', 'rejected']
    submitted_at: datetime


class ApplicationList(BaseModel):
    items: list[Application]
    next_cursor: int | None


class ApplicationUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['approved', 'rejected']


class RiskPrediction(BaseModel):
    id: int
    application_id: int
    default_probability: float = Field(ge=0, le=1)
    model_version: str
    created_at: datetime


def pagination(limit, after):
    try:
        page_size = int(limit)
        cursor = int(after) if after is not None else None
        if not 1 <= page_size <= 100 or (cursor is not None and cursor < 1):
            raise ValueError
    except ValueError:
        raise HTTPException(400, 'limit must be 1..100 and after must be a positive integer') from None
    return page_size, cursor


@router.post('/applications', response_model=Application, status_code=201)
def create_application(body: ApplicationCreate, request: Request, response: Response):
    store = request.app.state.store
    if not store.borrower(body.borrower_id):
        raise HTTPException(404, 'Borrower not found')
    application = store.create(body.model_dump())
    response.headers['Location'] = str(request.url_for('get_application', application_id=application['id']))
    return application


@router.get('/applications', response_model=ApplicationList)
def list_applications(request: Request, status: str | None = None, province: str | None = None,
                      limit: str = '20', after: str | None = None):
    size, cursor = pagination(limit, after)
    if status is not None and status not in ('pending', 'approved', 'rejected'):
        raise HTTPException(400, 'Invalid application status')
    return request.app.state.store.list(size, cursor, status, province)


@router.get('/applications/{application_id}', response_model=Application)
def get_application(application_id: Identifier, request: Request):
    row = request.app.state.store.get(application_id)
    if row is None:
        raise HTTPException(404, 'Application not found')
    return row


@router.patch('/applications/{application_id}', response_model=Application)
def update_application(application_id: Identifier, body: ApplicationUpdate, request: Request):
    changed, row = request.app.state.store.decide(application_id, body.status)
    if row is None:
        raise HTTPException(404, 'Application not found')
    if changed != 1:
        raise HTTPException(409, 'Application has already been decided')
    return row


@router.get('/borrowers/{borrower_id}/applications', response_model=ApplicationList)
def borrower_applications(borrower_id: Identifier, request: Request, limit: str = '20', after: str | None = None):
    size, cursor = pagination(limit, after)
    if request.app.state.store.borrower(borrower_id) is None:
        raise HTTPException(404, 'Borrower not found')
    return request.app.state.store.list(size, cursor, borrower_id=borrower_id)


@router.post('/applications/{application_id}/predictions', response_model=RiskPrediction, status_code=201)
def create_risk_prediction(application_id: Identifier, request: Request):
    store = request.app.state.store
    application = store.get(application_id)
    if application is None:
        raise HTTPException(404, 'Application not found')
    borrower = store.borrower(application['borrower_id'])
    model = request.app.state.champion
    features = {**borrower, **application}
    try:
        probability = model.predict(features)
    except (KeyError, TypeError, ValueError):
        raise HTTPException(422, 'Application is missing required risk-model inputs') from None
    return store.prediction(application_id, probability, model.version)
