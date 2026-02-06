from sqlalchemy.orm import Session
from ..models import ActionLog, ActionProposal, Campaign


def propose_action(db: Session, user_id: int, action_type: str, campaign_id: int):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise ValueError("Campaign not found")
    approval_required = campaign.budget_daily > 5000
    preview = f"{action_type} would set campaign '{campaign.name}' status from {campaign.status}."
    proposal = ActionProposal(
        requested_by=user_id,
        action_type=action_type,
        target_campaign_id=campaign_id,
        approval_required=approval_required,
        impact_preview=preview,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


def execute_action(db: Session, user_id: int, proposal_id: int):
    proposal = db.query(ActionProposal).filter(ActionProposal.id == proposal_id).first()
    if not proposal:
        raise ValueError("Proposal not found")
    campaign = db.query(Campaign).filter(Campaign.id == proposal.target_campaign_id).first()
    before = {"status": campaign.status}
    if proposal.action_type == "pause_campaign":
        campaign.status = "paused"
    elif proposal.action_type == "resume_campaign":
        campaign.status = "active"
    proposal.status = "executed"
    log = ActionLog(
        user_id=user_id,
        action_type=proposal.action_type,
        target_id=campaign.id,
        payload_before=before,
        payload_after={"status": campaign.status},
        reason="Executed via proposal",
    )
    db.add(log)
    db.commit()
    return log
