"""
Alert System Module
===================
Send push notifications for critical events using ntfy.sh.

Features:
- Push notifications via ntfy.sh (free, no signup needed)
- Priority levels (min, low, default, high, urgent)
- Emoji tags for quick visual identification
- Configurable alert triggers

Setup:
1. Subscribe to your topic:
   - Visit: https://ntfy.sh/YOUR-TOPIC-NAME (in browser or phone)
   - Or install ntfy app (iOS/Android) and subscribe to your topic
2. Set NTFY_TOPIC in config.py or environment variable
3. Test with: python -c "from utils.alerts import AlertSystem; AlertSystem().test_alert()"

Security Note:
- Use a PRIVATE topic name (random, hard to guess)
- Example: hickeylab-alerts-x9k2m7 (not hickeylab-alerts)
- Or self-host ntfy for full privacy control
"""

import os
from typing import Optional, List
from datetime import datetime


class AlertSystem:
    """Sends push notifications via ntfy.sh."""
    
    # Priority levels
    PRIORITY_MIN = "min"
    PRIORITY_LOW = "low"
    PRIORITY_DEFAULT = "default"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"
    
    def __init__(
        self,
        topic: Optional[str] = None,
        enabled: bool = True
    ):
        """
        Initialize alert system.
        
        Args:
            topic: ntfy.sh topic name (or set NTFY_TOPIC env variable)
            enabled: Set to False to disable alerts (useful for dev/testing)
        """
        self.topic = topic or os.getenv("NTFY_TOPIC", "")
        self.enabled = enabled and bool(self.topic)
        
        if self.enabled:
            self.ntfy_url = f"https://ntfy.sh/{self.topic}"
        else:
            self.ntfy_url = None
    
    def send_alert(
        self,
        title: str,
        message: str,
        priority: str = PRIORITY_DEFAULT,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Send a push notification.
        
        Args:
            title: Alert title
            message: Alert message body
            priority: Priority level (min, low, default, high, urgent)
            tags: List of emoji tags (e.g., ["warning", "rotating_light"])
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            import requests
            
            headers = {
                "Title": title,
                "Priority": priority,
            }
            
            if tags:
                headers["Tags"] = ",".join(tags)
            
            response = requests.post(
                self.ntfy_url,
                data=message.encode("utf-8"),
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            # Don't fail the app if alerts fail
            print(f"Warning: Failed to send alert: {e}")
            return False
    
    def alert_rate_limit_hit(self, session_id: str, count: int, limit_type: str) -> bool:
        """Alert when a user hits rate limit."""
        return self.send_alert(
            title="⚠️ Rate Limit Hit",
            message=f"Session {session_id[:8]} hit {limit_type} rate limit ({count} queries)",
            priority=self.PRIORITY_HIGH,
            tags=["warning"]
        )
    
    def alert_global_limit_hit(self, count: int, limit_type: str) -> bool:
        """Alert when global limit is reached (critical)."""
        return self.send_alert(
            title="🚨 GLOBAL LIMIT - Service Paused",
            message=f"Global {limit_type} limit reached: {count} queries. Service auto-paused.",
            priority=self.PRIORITY_URGENT,
            tags=["rotating_light", "stop_sign"]
        )
    
    def alert_suspicious_activity(self, session_id: str, reason: str) -> bool:
        """Alert about suspicious/malicious activity."""
        return self.send_alert(
            title="🔍 Suspicious Activity",
            message=f"Session {session_id[:8]}: {reason}",
            priority=self.PRIORITY_HIGH,
            tags=["mag", "warning"]
        )
    
    def alert_cost_threshold(self, current_cost: float, threshold: float, period: str) -> bool:
        """Alert when cost threshold is reached."""
        percentage = (current_cost / threshold) * 100
        return self.send_alert(
            title="💰 Cost Alert",
            message=f"{period.capitalize()} cost: ${current_cost:.2f} ({percentage:.0f}% of ${threshold:.2f} budget)",
            priority=self.PRIORITY_HIGH if percentage >= 100 else self.PRIORITY_DEFAULT,
            tags=["money_with_wings", "warning"] if percentage >= 100 else ["money_with_wings"]
        )
    
    def alert_error_spike(self, error_count: int, time_window: str) -> bool:
        """Alert about error spikes."""
        return self.send_alert(
            title="⚠️ Error Spike Detected",
            message=f"{error_count} errors in {time_window}",
            priority=self.PRIORITY_HIGH,
            tags=["warning", "fire"]
        )
    
    def test_alert(self) -> bool:
        """Send a test alert to verify configuration."""
        if not self.enabled:
            print("❌ Alerts are disabled. Set NTFY_TOPIC to enable.")
            return False
        
        success = self.send_alert(
            title="✅ Test Alert",
            message=f"Alert system configured successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            priority=self.PRIORITY_LOW,
            tags=["white_check_mark"]
        )
        
        if success:
            print(f"✅ Test alert sent to topic: {self.topic}")
            print(f"   View at: https://ntfy.sh/{self.topic}")
        else:
            print("❌ Failed to send test alert")
        
        return success


# Convenience function for quick testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        topic = os.getenv("NTFY_TOPIC")
    
    if not topic:
        print("Usage: python alerts.py <topic-name>")
        print("   Or: Set NTFY_TOPIC environment variable")
        sys.exit(1)
    
    alert_system = AlertSystem(topic=topic)
    alert_system.test_alert()
