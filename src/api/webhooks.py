from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.webhook import WebhookSubscription
from src.schemas.webhook import WebhookCreate, WebhookResponse
from src.schemas.base import APIResponse
from src.api.dependencies import verify_api_key

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("", response_model=APIResponse[WebhookResponse], status_code=status.HTTP_201_CREATED)
def register_webhook(
    hook: WebhookCreate, 
    db: Session = Depends(get_db), 
    user=Depends(verify_api_key)
):
    db_hook = WebhookSubscription(target_url=str(hook.target_url))
    db.add(db_hook)
    db.commit()
    db.refresh(db_hook)
    
    return APIResponse(success=True, data=db_hook)

@router.get("", response_model=APIResponse[list[WebhookResponse]])
def get_webhooks(
    db: Session = Depends(get_db),
    user=Depends(verify_api_key)
):
    hooks = db.query(WebhookSubscription).filter(WebhookSubscription.is_active == True).all()
    return APIResponse(success=True, data=hooks)

@router.delete("/{hook_id}", response_model=APIResponse[dict])
def delete_webhook(
    hook_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_api_key)
):
    hook = db.query(WebhookSubscription).filter(WebhookSubscription.id == hook_id).first()
    if not hook:
        raise HTTPException(status_code=404, detail="Webhook not found")
        
    hook.is_active = False
    db.commit()
    
    return APIResponse(success=True, data={"message": "Webhook deleted"})
