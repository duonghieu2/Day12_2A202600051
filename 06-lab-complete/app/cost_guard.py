import time
from datetime import datetime, timezone
from fastapi import HTTPException
from app.rate_limiter import r
from app.config import settings

def check_and_record_cost(user_id: str, input_tokens: int, output_tokens: int):
    """
    Check if the user has exceeded their monthly budget.
    We track budget per Month.
    """
    if not r:
        return # Skip budget checking if no Redis
    
    month_str = datetime.now(timezone.utc).strftime("%Y-%m")
    key = f"budget:{user_id}:{month_str}"
    
    cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006
    
    amount_used = float(r.get(key) or 0.0)
    
    if amount_used + cost > settings.daily_budget_usd: # Here budget config is per month/daily depending on settings
        raise HTTPException(
            status_code=402,
            detail="Budget exhausted. Please try again later.",
        )
    
    if cost > 0:
        pipeline = r.pipeline()
        pipeline.incrbyfloat(key, cost)
        pipeline.expire(key, 32 * 24 * 3600)  # Keep for ~32 days max
        pipeline.execute()
