from datetime import date, timedelta
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import ActionLog, Anomaly, Brand, Campaign, MetricDefinition, MetricSnapshot, Organization, User
from .schemas import (
    ActionExecuteRequest,
    ActionProposalRequest,
    AnomalyStatusRequest,
    ChatMessageRequest,
    LoginRequest,
    MetricDefinitionRequest,
    MetricsQueryRequest,
)
from .services.action_service import execute_action, propose_action
from .services.anomaly_service import detect_ctr_anomalies
from .services.chat_service import handle_chat
from .services.metrics_service import query_metrics

app = FastAPI(title="Marketing Analyst AI API")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db:
        if db.query(Organization).count() == 0:
            seed(db)


def seed(db: Session):
    org = Organization(name="Demo Pharma")
    db.add(org)
    db.flush()
    db.add_all([
        User(org_id=org.id, name="Alice Manager", email="manager@demo.com", role="manager", brand_scope="all"),
        User(org_id=org.id, name="Bob Viewer", email="viewer@demo.com", role="viewer", brand_scope="Brand A"),
    ])
    brand = Brand(org_id=org.id, name="Brand A", therapeutic_area="Oncology")
    db.add(brand)
    db.flush()
    campaigns = [
        Campaign(org_id=org.id, brand_id=brand.id, channel="Google Ads", name="HCP Search", budget_daily=3000, owner="Alice", region="US"),
        Campaign(org_id=org.id, brand_id=brand.id, channel="LinkedIn", name="Awareness Video", budget_daily=7000, owner="Alice", region="US"),
    ]
    db.add_all(campaigns)
    db.flush()
    for c in campaigns:
        for i in range(30):
            dt = date.today() - timedelta(days=(29 - i))
            base_impr = 10000 if c.channel == "Google Ads" else 8000
            clicks = 380 if c.channel == "Google Ads" else 160
            if i == 29 and c.channel == "LinkedIn":
                clicks = 40
            db.add(MetricSnapshot(date=dt, campaign_id=c.id, impressions=base_impr, clicks=clicks, spend=1500 + i * 15, conversions=max(2, clicks // 50)))
    db.add_all([
        MetricDefinition(metric_name="impressions", formula="sum(impressions)", allowed_dims=["campaign", "channel", "date"]),
        MetricDefinition(metric_name="clicks", formula="sum(clicks)", allowed_dims=["campaign", "channel", "date"]),
        MetricDefinition(metric_name="spend", formula="sum(spend)", allowed_dims=["campaign", "channel", "date"]),
        MetricDefinition(metric_name="conversions", formula="sum(conversions)", allowed_dims=["campaign", "channel", "date"]),
        MetricDefinition(metric_name="ctr", formula="sum(clicks)/sum(impressions)", allowed_dims=["campaign", "channel", "date"]),
        MetricDefinition(metric_name="cpc", formula="sum(spend)/sum(clicks)", allowed_dims=["campaign", "channel", "date"]),
    ])
    db.commit()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(401, "User not found")
    return {"token": f"dev-token-{user.id}", "user": {"id": user.id, "name": user.name, "role": user.role, "email": user.email}}


@app.get("/auth/me")
def me(db: Session = Depends(get_db)):
    user = db.query(User).first()
    return {"id": user.id, "name": user.name, "role": user.role, "email": user.email}


@app.post("/metrics/query")
def metrics_query(payload: MetricsQueryRequest, db: Session = Depends(get_db)):
    try:
        return query_metrics(db, payload.metric, payload.dimensions, payload.filters, payload.date_range)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/metrics/definitions")
def list_metric_definitions(db: Session = Depends(get_db)):
    return db.query(MetricDefinition).all()


@app.post("/metrics/definitions")
def create_metric_definition(payload: MetricDefinitionRequest, db: Session = Depends(get_db)):
    md = MetricDefinition(**payload.model_dump())
    db.add(md)
    db.commit()
    return {"status": "created", "id": md.id}


@app.get("/campaigns")
def list_campaigns(channel: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Campaign)
    if channel:
        q = q.filter(Campaign.channel == channel)
    return q.all()


@app.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Not found")
    metrics = db.query(MetricSnapshot).filter(MetricSnapshot.campaign_id == campaign_id).order_by(MetricSnapshot.date.asc()).all()
    return {"campaign": campaign, "metrics": metrics}


@app.post("/campaigns/{campaign_id}/pause")
def pause_campaign(campaign_id: int, db: Session = Depends(get_db)):
    proposal = propose_action(db, 1, "pause_campaign", campaign_id)
    return {"proposal_id": proposal.id, "impact_preview": proposal.impact_preview, "approval_required": proposal.approval_required}


@app.post("/campaigns/{campaign_id}/resume")
def resume_campaign(campaign_id: int, db: Session = Depends(get_db)):
    proposal = propose_action(db, 1, "resume_campaign", campaign_id)
    return {"proposal_id": proposal.id, "impact_preview": proposal.impact_preview, "approval_required": proposal.approval_required}


@app.post("/actions/propose")
def actions_propose(payload: ActionProposalRequest, db: Session = Depends(get_db)):
    p = propose_action(db, 1, payload.action_type, payload.campaign_id)
    return {"proposal_id": p.id, "impact_preview": p.impact_preview, "approval_required": p.approval_required}


@app.post("/actions/execute")
def actions_execute(payload: ActionExecuteRequest, db: Session = Depends(get_db)):
    log = execute_action(db, 1, payload.proposal_id)
    return {"action_id": log.id, "target_id": log.target_id, "status": log.payload_after}


@app.get("/anomalies")
def list_anomalies(status: str | None = None, severity: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Anomaly)
    if status:
        q = q.filter(Anomaly.status == status)
    if severity:
        q = q.filter(Anomaly.severity == severity)
    return q.order_by(Anomaly.detected_at.desc()).all()


@app.post("/anomalies/run")
def run_anomalies(db: Session = Depends(get_db)):
    created = detect_ctr_anomalies(db)
    return {"created": created}


@app.get("/anomalies/{anomaly_id}")
def get_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(404, "Not found")
    return anomaly


@app.post("/anomalies/{anomaly_id}/acknowledge")
def acknowledge_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    anomaly.status = "acknowledged"
    db.commit()
    return {"status": anomaly.status}


@app.post("/anomalies/{anomaly_id}/resolve")
def resolve_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    anomaly.status = "resolved"
    db.commit()
    return {"status": anomaly.status}


@app.post("/chat/message")
def chat_message(payload: ChatMessageRequest, db: Session = Depends(get_db)):
    return handle_chat(db, 1, payload.message)


@app.get("/audit/actions")
def audit_actions(db: Session = Depends(get_db)):
    return db.query(ActionLog).order_by(ActionLog.timestamp.desc()).all()


@app.get("/audit/actions/{action_id}")
def audit_action(action_id: int, db: Session = Depends(get_db)):
    return db.query(ActionLog).filter(ActionLog.id == action_id).first()
