from statistics import median
from sqlalchemy.orm import Session
from ..models import Anomaly, Campaign, MetricSnapshot


def detect_ctr_anomalies(db: Session):
    campaigns = db.query(Campaign).all()
    created = 0
    for campaign in campaigns:
        snapshots = (
            db.query(MetricSnapshot)
            .filter(MetricSnapshot.campaign_id == campaign.id)
            .order_by(MetricSnapshot.date.asc())
            .all()
        )
        if len(snapshots) < 7:
            continue
        ctr_series = [s.clicks / s.impressions if s.impressions else 0 for s in snapshots]
        baseline = median(ctr_series[:-1])
        abs_dev = [abs(v - baseline) for v in ctr_series[:-1]]
        mad = median(abs_dev) or 0.0001
        latest = ctr_series[-1]
        robust_z = (latest - baseline) / (1.4826 * mad)
        if abs(robust_z) > 3 and abs(latest - baseline) > 0.01:
            anomaly = Anomaly(
                severity="high" if abs(robust_z) > 5 else "medium",
                campaign_id=campaign.id,
                metric="ctr",
                observed_value=latest,
                expected_low=baseline - (3 * mad),
                expected_high=baseline + (3 * mad),
                explanation=f"CTR deviation detected with robust z-score {robust_z:.2f}",
            )
            db.add(anomaly)
            created += 1
    db.commit()
    return created
