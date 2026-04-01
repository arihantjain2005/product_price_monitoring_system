from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.auth import ApiUser, ApiUsage

def verify_api_key(request: Request, db: Session = Depends(get_db)):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key header")
    
    user = db.query(ApiUser).filter(ApiUser.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    
    # Rate Limiting Logic: Max 60 requests per minute
    from datetime import datetime, timezone, timedelta
    one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
    
    recent_requests = db.query(ApiUsage).filter(
        ApiUsage.api_user_id == user.id,
        ApiUsage.timestamp >= one_minute_ago
    ).count()

    if recent_requests >= 60:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded. Maximum 60 requests per minute.")

    usage_entry = ApiUsage(
        api_user_id=user.id,
        endpoint=request.url.path,
        method=request.method
    )
    db.add(usage_entry)
    db.commit()
    
    return user
