from datetime import date, datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str


class MetricsQueryRequest(BaseModel):
    metric: str
    dimensions: list[str] = Field(default_factory=lambda: ["campaign"])
    filters: dict = Field(default_factory=dict)
    date_range: dict


class ActionRequest(BaseModel):
    campaign_id: int
    reason: str = ""


class ActionProposalRequest(BaseModel):
    action_type: str
    campaign_id: int


class ActionExecuteRequest(BaseModel):
    proposal_id: int


class ChatMessageRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    assumptions: list[str]
    time_range: dict
    filters: dict
    data_freshness: dict
    tables: list[dict]
    charts: list[dict]
    recommended_actions: list[dict]
    confidence: str


class AnomalyStatusRequest(BaseModel):
    status: str


class MetricDefinitionRequest(BaseModel):
    metric_name: str
    formula: str
    allowed_dims: list[str]
    owner: str = "marketing-ops"
    version: str = "v1"
