from datetime import date, datetime
from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    timezone: Mapped[str] = mapped_column(String(60), default="UTC")
    currency: Mapped[str] = mapped_column(String(10), default="USD")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    role: Mapped[str] = mapped_column(String(30), default="viewer")
    brand_scope: Mapped[str] = mapped_column(String(120), default="all")
    password_hash: Mapped[str] = mapped_column(String(255), default="dev")


class Brand(Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String(120))
    therapeutic_area: Mapped[str] = mapped_column(String(120), default="General")


class Campaign(Base):
    __tablename__ = "campaigns"
    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    channel: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(200))
    objective: Mapped[str] = mapped_column(String(80), default="awareness")
    status: Mapped[str] = mapped_column(String(30), default="active")
    budget_daily: Mapped[float] = mapped_column(Float, default=1000)
    owner: Mapped[str] = mapped_column(String(80), default="unassigned")
    region: Mapped[str] = mapped_column(String(80), default="Global")


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    spend: Mapped[float] = mapped_column(Float, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    ingestion_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MetricDefinition(Base):
    __tablename__ = "metric_definitions"
    id: Mapped[int] = mapped_column(primary_key=True)
    metric_name: Mapped[str] = mapped_column(String(60), unique=True)
    formula: Mapped[str] = mapped_column(String(255))
    allowed_dims: Mapped[dict] = mapped_column(JSON, default=["campaign", "channel", "date"])
    owner: Mapped[str] = mapped_column(String(80), default="marketing-ops")
    version: Mapped[str] = mapped_column(String(20), default="v1")


class Anomaly(Base):
    __tablename__ = "anomalies"
    id: Mapped[int] = mapped_column(primary_key=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    severity: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="new")
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    metric: Mapped[str] = mapped_column(String(40))
    observed_value: Mapped[float] = mapped_column(Float)
    expected_low: Mapped[float] = mapped_column(Float)
    expected_high: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(Text)


class ActionLog(Base):
    __tablename__ = "action_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    action_type: Mapped[str] = mapped_column(String(40))
    target_type: Mapped[str] = mapped_column(String(40), default="campaign")
    target_id: Mapped[int] = mapped_column(Integer)
    payload_before: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    payload_after: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    approval_status: Mapped[str] = mapped_column(String(20), default="approved")
    reason: Mapped[str] = mapped_column(String(255), default="")


class ActionProposal(Base):
    __tablename__ = "action_proposals"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action_type: Mapped[str] = mapped_column(String(40))
    target_campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    impact_preview: Mapped[str] = mapped_column(Text)
    approval_required: Mapped[bool] = mapped_column(Boolean, default=False)
