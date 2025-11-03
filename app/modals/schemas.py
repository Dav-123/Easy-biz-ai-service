from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class GenerationType(str, Enum):
    BRAND_KIT = "brand_kit"
    SOCIAL_MEDIA = "social_media"
    WEBSITE_CONTENT = "website_content"
    BUSINESS_PLAN = "business_plan"
    IMAGE_GENERATION = "image_generation"

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationRequest(BaseModel):
    project_id: str
    generation_type: GenerationType
    prompts: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    available_services: Dict[str, bool]