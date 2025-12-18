"""
Rate Limiting Module
====================
Prevents abuse and ensures fair usage through rate limiting.

Features:
- Session-based rate limiting
- Time-window based tracking (sliding window)
- User-friendly warnings before limits hit
- Configurable soft and hard limits
- Logging of rate limit violations

Configuration:
- Set limits in config.py
- Adjust WARNING_THRESHOLD for when to show warnings
"""

from datetime import datetime, timedelta
from typing import Tuple, Optional
import json
from pathlib import Path


class RateLimiter:
    """Manages rate limiting for chat queries."""
    
    def __init__(
        self,
        max_per_hour: int = 20,
        max_per_day: int = 200,
        warning_threshold: float = 0.8,
        log_dir: str = "logs"
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_per_hour: Maximum queries allowed per hour
            max_per_day: Maximum queries allowed per 24 hours
            warning_threshold: Fraction at which to show warning (0.8 = 80%)
            log_dir: Directory for rate limit violation logs
        """
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.warning_threshold = warning_threshold
        
        self.log_dir = Path(log_dir)
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            # Fallback to temp directory
            import tempfile
            self.log_dir = Path(tempfile.gettempdir()) / "hickeylab_logs"
            self.log_dir.mkdir(parents=True, exist_ok=True)
        self.violation_log = self.log_dir / "rate_limits.jsonl"
    
    def check_rate_limit(
        self,
        query_times: list,
        session_id: str
    ) -> Tuple[bool, Optional[str], int]:
        """
        Check if request is within rate limits.
        
        Args:
            query_times: List of datetime objects for previous queries
            session_id: Unique session identifier
        
        Returns:
            Tuple of (allowed, message, remaining_queries)
            - allowed: True if request should be allowed
            - message: User-facing message (warning or error)
            - remaining_queries: Number of queries remaining in current window
        """
        now = datetime.now()
        
        # Remove queries older than 24 hours
        recent_queries = [
            t for t in query_times 
            if now - t < timedelta(hours=24)
        ]
        
        # Remove queries older than 1 hour
        hourly_queries = [
            t for t in recent_queries
            if now - t < timedelta(hours=1)
        ]
        
        # Check hourly limit
        hourly_count = len(hourly_queries)
        hourly_remaining = self.max_per_hour - hourly_count
        
        if hourly_count >= self.max_per_hour:
            self._log_violation(session_id, "hourly", hourly_count)
            oldest_hourly = min(hourly_queries)
            retry_after = oldest_hourly + timedelta(hours=1) - now
            minutes = int(retry_after.total_seconds() / 60)
            message = (
                f"🕐 **Rate limit reached!**\n\n"
                f"You've reached the limit of {self.max_per_hour} questions per hour. "
                f"Please wait **{minutes} minutes** before asking another question.\n\n"
                f"This limit helps us manage costs and ensure the service stays available for everyone."
            )
            return False, message, 0
        
        # Check daily limit
        daily_count = len(recent_queries)
        daily_remaining = self.max_per_day - daily_count
        
        if daily_count >= self.max_per_day:
            self._log_violation(session_id, "daily", daily_count)
            message = (
                f"📅 **Daily limit reached!**\n\n"
                f"You've reached the daily limit of {self.max_per_day} questions. "
                f"Please come back tomorrow!\n\n"
                f"This limit helps us manage costs and keep the service available for everyone."
            )
            return False, message, 0
        
        # Check if approaching limits (warning)
        hourly_usage_pct = hourly_count / self.max_per_hour
        
        if hourly_usage_pct >= self.warning_threshold:
            warning_msg = (
                f"⚠️ You have **{hourly_remaining} questions** remaining this hour "
                f"({hourly_count}/{self.max_per_hour} used)."
            )
            return True, warning_msg, hourly_remaining
        
        # All good
        return True, None, min(hourly_remaining, daily_remaining)
    
    def _log_violation(self, session_id: str, limit_type: str, count: int) -> None:
        """Log a rate limit violation."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id[:8] if len(session_id) >= 8 else session_id,
            "limit_type": limit_type,
            "query_count": count
        }
        
        try:
            with open(self.violation_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except (IOError, OSError) as e:
            # Don't crash if logging fails
            print(f"Warning: Could not log rate limit violation: {e}")
