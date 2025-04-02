from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ValidationError(BaseModel):
    loc: List[str]
    msg: str
    type: str
    ctx: Optional[Dict[str, Any]] = None

class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = None 