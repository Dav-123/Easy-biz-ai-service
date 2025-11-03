import uuid
import time
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
import json
import hashlib
import random
import string

def generate_id(prefix: str = "", length: int = 16) -> str:
    """
    Generate a unique ID with optional prefix.
    """
    unique_id = uuid.uuid4().hex[:length]
    return f"{prefix}_{unique_id}" if prefix else unique_id

def format_timestamp(timestamp: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string.
    """
    return timestamp.strftime(format_str)

def parse_timestamp(timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse string to datetime object.
    """
    return datetime.strptime(timestamp_str, format_str)

def calculate_quota_usage(
    total_quota: int, 
    used_quota: int, 
    current_usage: int = 0
) -> Dict[str, Any]:
    """
    Calculate quota usage and remaining quota.
    """
    remaining = total_quota - used_quota - current_usage
    percentage_used = (used_quota + current_usage) / total_quota * 100
    
    return {
        "total_quota": total_quota,
        "used_quota": used_quota,
        "current_usage": current_usage,
        "remaining_quota": max(0, remaining),
        "percentage_used": round(percentage_used, 2),
        "will_exceed_quota": remaining < 0
    }

async def retry_operation(
    operation: Callable,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Retry an operation with exponential backoff.
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(operation):
                return await operation()
            else:
                return operation()
                
        except exceptions as e:
            last_exception = e
            if attempt == max_retries:
                break
                
            sleep_time = delay * (backoff ** attempt)
            await asyncio.sleep(sleep_time)
    
    raise last_exception

def generate_random_string(length: int = 8, include_digits: bool = True) -> str:
    """
    Generate a random string of specified length.
    """
    characters = string.ascii_letters
    if include_digits:
        characters += string.digits
    
    return ''.join(random.choice(characters) for _ in range(length))

def hash_data(data: str, algorithm: str = 'sha256') -> str:
    """
    Hash data using specified algorithm.
    """
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode('utf-8'))
    return hasher.hexdigest()

def safe_json_parse(data: str, default: Any = None) -> Any:
    """
    Safely parse JSON data with default fallback.
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default

def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Recursively merge two dictionaries.
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if (key in result and isinstance(result[key], dict) 
            and isinstance(value, dict)):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def get_time_ago(timestamp: datetime) -> str:
    """
    Get human-readable time difference from now.
    """
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"

def validate_email(email: str) -> bool:
    """
    Basic email validation.
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing unsafe characters.
    """
    import re
    # Remove characters that are not safe in filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    return sanitized[:255]

class RateLimiter:
    """
    Simple rate limiter implementation.
    """
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def is_allowed(self) -> bool:
        """
        Check if request is allowed based on rate limit.
        """
        now = time.time()
        
        # Remove requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
    
    def get_retry_after(self) -> float:
        """
        Get time until next allowed request.
        """
        if not self.requests:
            return 0.0
        
        now = time.time()
        oldest_request = self.requests[0]
        return max(0.0, self.time_window - (now - oldest_request))