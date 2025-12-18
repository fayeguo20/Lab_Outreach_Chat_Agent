"""
Cost Management Module
======================
Tracks API token usage and costs to prevent budget overruns.

Features:
- Real-time token counting from Gemini API responses
- Cost calculation based on Gemini pricing
- Daily/monthly usage tracking
- Budget cap enforcement
- Usage reporting and analytics

Configuration:
- Set DAILY_QUERY_LIMIT and MONTHLY_BUDGET_USD in config.py
- Logs are saved to logs/usage.jsonl
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
from collections import defaultdict


# Pricing for Gemini 2.5 Flash (per 1M tokens)
INPUT_COST_PER_1M = 0.075   # $0.075 per 1M input tokens
OUTPUT_COST_PER_1M = 0.30   # $0.30 per 1M output tokens


class CostTracker:
    """Tracks API usage and costs."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize cost tracker with log directory."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.usage_log = self.log_dir / "usage.jsonl"
    
    def calculate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Calculate cost for a query based on token usage."""
        input_cost = (prompt_tokens / 1_000_000) * INPUT_COST_PER_1M
        output_cost = (response_tokens / 1_000_000) * OUTPUT_COST_PER_1M
        return input_cost + output_cost
    
    def log_usage(
        self,
        session_id: str,
        question_length: int,
        prompt_tokens: int,
        response_tokens: int,
        total_tokens: int,
        response_time: float,
        success: bool = True,
        error_msg: Optional[str] = None
    ) -> None:
        """Log a query's usage data."""
        cost = self.calculate_cost(prompt_tokens, response_tokens)
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id[:8],  # Truncated for privacy
            "question_length": question_length,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(cost, 6),
            "response_time_ms": int(response_time * 1000),
            "success": success,
            "error": error_msg
        }
        
        with open(self.usage_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_usage_stats(self, date: Optional[datetime] = None) -> Dict:
        """Get usage statistics for a specific date (defaults to today)."""
        if date is None:
            date = datetime.utcnow().date()
        else:
            date = date.date()
        
        target_date = date.isoformat()
        stats = defaultdict(int)
        stats["date"] = target_date
        
        if not self.usage_log.exists():
            return dict(stats)
        
        with open(self.usage_log) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry["timestamp"].startswith(target_date):
                        stats["queries"] += 1
                        stats["prompt_tokens"] += entry["prompt_tokens"]
                        stats["response_tokens"] += entry["response_tokens"]
                        stats["total_tokens"] += entry["total_tokens"]
                        stats["total_cost"] += entry["estimated_cost_usd"]
                        if entry["success"]:
                            stats["successful_queries"] += 1
                        else:
                            stats["failed_queries"] += 1
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return dict(stats)
    
    def get_monthly_stats(self, year: int, month: int) -> Dict:
        """Get usage statistics for an entire month."""
        target_month = f"{year:04d}-{month:02d}"
        stats = defaultdict(int)
        stats["month"] = target_month
        
        if not self.usage_log.exists():
            return dict(stats)
        
        with open(self.usage_log) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry["timestamp"].startswith(target_month):
                        stats["queries"] += 1
                        stats["total_cost"] += entry["estimated_cost_usd"]
                        stats["total_tokens"] += entry["total_tokens"]
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return dict(stats)
    
    def check_daily_limit(self, daily_limit: int = 200) -> Tuple[bool, int]:
        """
        Check if daily query limit has been reached.
        
        Returns:
            Tuple of (within_limit, current_count)
        """
        today_stats = self.get_usage_stats()
        current_count = today_stats.get("queries", 0)
        return current_count < daily_limit, current_count
    
    def check_monthly_budget(self, monthly_budget: float = 50.0) -> Tuple[bool, float]:
        """
        Check if monthly budget has been exceeded.
        
        Returns:
            Tuple of (within_budget, current_cost)
        """
        now = datetime.utcnow()
        monthly_stats = self.get_monthly_stats(now.year, now.month)
        current_cost = monthly_stats.get("total_cost", 0.0)
        return current_cost < monthly_budget, current_cost
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> str:
        """Generate a human-readable daily usage report."""
        stats = self.get_usage_stats(date)
        
        if stats.get("queries", 0) == 0:
            return f"=== Daily Report: {stats['date']} ===\nNo queries recorded."
        
        report = f"""=== Daily Report: {stats['date']} ===
Queries: {stats.get('queries', 0)}
  ├─ Successful: {stats.get('successful_queries', 0)}
  └─ Failed: {stats.get('failed_queries', 0)}

Token Usage:
  ├─ Prompt tokens: {stats.get('prompt_tokens', 0):,}
  ├─ Response tokens: {stats.get('response_tokens', 0):,}
  └─ Total tokens: {stats.get('total_tokens', 0):,}

Estimated Cost: ${stats.get('total_cost', 0):.4f}
Average Cost per Query: ${stats.get('total_cost', 0) / max(stats.get('queries', 1), 1):.6f}
"""
        return report
    
    def generate_monthly_report(self, year: int, month: int) -> str:
        """Generate a human-readable monthly usage report."""
        stats = self.get_monthly_stats(year, month)
        
        if stats.get("queries", 0) == 0:
            return f"=== Monthly Report: {stats['month']} ===\nNo queries recorded."
        
        report = f"""=== Monthly Report: {stats['month']} ===
Total Queries: {stats.get('queries', 0)}
Total Tokens: {stats.get('total_tokens', 0):,}
Total Cost: ${stats.get('total_cost', 0):.2f}
Average Cost per Query: ${stats.get('total_cost', 0) / max(stats.get('queries', 1), 1):.6f}
"""
        return report
