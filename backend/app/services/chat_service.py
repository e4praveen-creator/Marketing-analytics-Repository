from datetime import date, timedelta
from sqlalchemy.orm import Session
from .action_service import propose_action
from .metrics_service import query_metrics


def handle_chat(db: Session, user_id: int, message: str):
    text = message.lower().strip()
    today = date.today()
    default_range = {"start": str(today - timedelta(days=6)), "end": str(today)}

    if text.startswith("pause campaign"):
        try:
            campaign_id = int(text.split()[-1])
            proposal = propose_action(db, user_id, "pause_campaign", campaign_id)
            return {
                "answer": f"Proposed pause for campaign {campaign_id}. Please confirm execution.",
                "assumptions": ["Parsed trailing integer as campaign ID."],
                "time_range": default_range,
                "filters": {},
                "data_freshness": {"as_of": today.isoformat(), "status": "fresh"},
                "tables": [],
                "charts": [],
                "recommended_actions": [{"label": "Execute proposal", "proposal_id": proposal.id}],
                "confidence": "high",
            }
        except Exception:
            return {
                "answer": "I could not parse campaign id. Try: 'Pause campaign 1'.",
                "assumptions": ["No action executed."],
                "time_range": default_range,
                "filters": {},
                "data_freshness": {"as_of": today.isoformat(), "status": "fresh"},
                "tables": [],
                "charts": [],
                "recommended_actions": [],
                "confidence": "low",
            }

    metric = "ctr" if "ctr" in text else "spend" if "spend" in text else "clicks"
    result = query_metrics(db, metric, ["campaign"], {}, default_range)
    rows = [[r.get("campaign", ""), round((r.get(metric) or 0), 4)] for r in result["rows"][:10]]
    return {
        "answer": f"Here is {metric.upper()} for the last 7 days.",
        "assumptions": ["Defaulted date range to last 7 days.", "No brand/channel filters applied."],
        "time_range": default_range,
        "filters": {},
        "data_freshness": {"as_of": result["metadata"]["freshness"], "status": "fresh"},
        "tables": [{"title": f"{metric.upper()} by campaign", "columns": ["campaign", metric], "rows": rows}],
        "charts": [],
        "recommended_actions": [],
        "confidence": "high",
    }
