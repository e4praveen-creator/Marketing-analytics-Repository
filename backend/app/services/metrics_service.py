from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models import Campaign, MetricDefinition, MetricSnapshot

ALLOWED_METRICS = {
    "impressions": func.sum(MetricSnapshot.impressions),
    "clicks": func.sum(MetricSnapshot.clicks),
    "spend": func.sum(MetricSnapshot.spend),
    "conversions": func.sum(MetricSnapshot.conversions),
    "ctr": (func.sum(MetricSnapshot.clicks) * 1.0 / func.nullif(func.sum(MetricSnapshot.impressions), 0)),
    "cpc": (func.sum(MetricSnapshot.spend) * 1.0 / func.nullif(func.sum(MetricSnapshot.clicks), 0)),
}


def query_metrics(db: Session, metric: str, dimensions: list[str], filters: dict, date_range: dict):
    definition = db.query(MetricDefinition).filter(MetricDefinition.metric_name == metric).first()
    if not definition or metric not in ALLOWED_METRICS:
        raise ValueError(f"Metric '{metric}' is not defined.")
    invalid_dims = [d for d in dimensions if d not in definition.allowed_dims]
    if invalid_dims:
        raise ValueError(f"Dimensions not allowed for {metric}: {invalid_dims}")

    query = db.query(ALLOWED_METRICS[metric].label(metric))
    if "campaign" in dimensions or "channel" in dimensions:
        query = query.join(Campaign, Campaign.id == MetricSnapshot.campaign_id)
    if "campaign" in dimensions:
        query = query.add_columns(Campaign.name.label("campaign"))
    if "channel" in dimensions:
        query = query.add_columns(Campaign.channel.label("channel"))
    if "date" in dimensions:
        query = query.add_columns(MetricSnapshot.date.label("date"))

    query = query.filter(MetricSnapshot.date >= date_range["start"]).filter(MetricSnapshot.date <= date_range["end"])

    if filters.get("brand_id"):
        query = query.filter(Campaign.brand_id == filters["brand_id"])
    if filters.get("channel"):
        query = query.filter(Campaign.channel == filters["channel"])

    group_cols = []
    if "campaign" in dimensions:
        group_cols.append(Campaign.name)
    if "channel" in dimensions:
        group_cols.append(Campaign.channel)
    if "date" in dimensions:
        group_cols.append(MetricSnapshot.date)
    if group_cols:
        query = query.group_by(*group_cols)

    rows = query.all()
    payload = [dict(row._mapping) for row in rows]
    return {
        "rows": payload,
        "metadata": {
            "rowcount": len(payload),
            "freshness": datetime.utcnow().isoformat(),
            "metric": metric,
        },
    }
