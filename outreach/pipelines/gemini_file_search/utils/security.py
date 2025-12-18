"""
Security Module
===============
Input validation and sanitization to prevent abuse and attacks.

Features:
- Input length validation
- Prompt injection detection
- Suspicious pattern detection
- Logging of security violations

Configuration:
- Adjust MAX_INPUT_LENGTH and MIN_INPUT_LENGTH as needed
- Add custom suspicious patterns if needed
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional


class SecurityValidator:
    """Validates and sanitizes user input."""
    
    # Input length constraints
    MAX_INPUT_LENGTH = 2000
    MIN_INPUT_LENGTH = 1
    
    # Suspicious patterns that might indicate prompt injection or abuse
    SUSPICIOUS_PATTERNS = [
        r"ignore\s+(previous|all|your)\s+instructions",
        r"system\s*prompt",
        r"you\s+are\s+now",
        r"pretend\s+to\s+be",
        r"act\s+as\s+(a|an)",
        r"<script[^>]*>",
        r"javascript:",
        r"\{\{.*\}\}",  # Template injection
        r"reveal\s+(your|the)\s+(prompt|instructions)",
        r"disregard\s+(previous|all)",
        r"admin\s+mode",
        r"developer\s+mode",
    ]
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize security validator."""
        self.log_dir = Path(log_dir)
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            import tempfile
            self.log_dir = Path(tempfile.gettempdir()) / "hickeylab_logs"
            self.log_dir.mkdir(parents=True, exist_ok=True)
        self.security_log = self.log_dir / "security.jsonl"
    
    def validate_input(
        self,
        user_input: str,
        session_id: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Validate and sanitize user input.
        
        Args:
            user_input: The user's input text
            session_id: Unique session identifier for logging
        
        Returns:
            Tuple of (is_valid, cleaned_input, error_message)
            - is_valid: True if input passes all checks
            - cleaned_input: The cleaned/trimmed input
            - error_message: User-facing error message if invalid
        """
        # Strip whitespace
        cleaned = user_input.strip()
        
        # Check minimum length
        if len(cleaned) < self.MIN_INPUT_LENGTH:
            return False, "", "Please enter a question."
        
        # Check maximum length
        if len(cleaned) > self.MAX_INPUT_LENGTH:
            return (
                False,
                "",
                f"⚠️ Question too long. Please keep your question under {self.MAX_INPUT_LENGTH} characters. "
                f"(Current: {len(cleaned)} characters)"
            )
        
        # Check for suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                self._log_suspicious(session_id, cleaned, pattern)
                return (
                    False,
                    "",
                    "⚠️ Your question contains invalid content. Please rephrase and try again."
                )
        
        # Check for excessive special characters (might indicate injection attempt)
        special_char_ratio = len(re.findall(r"[^a-zA-Z0-9\s.,;:?!()\-']", cleaned)) / max(len(cleaned), 1)
        if special_char_ratio > 0.3:  # More than 30% special characters
            self._log_suspicious(session_id, cleaned, "excessive_special_chars")
            return (
                False,
                "",
                "⚠️ Your question contains unusual characters. Please use standard text."
            )
        
        # All checks passed
        return True, cleaned, None
    
    def _log_suspicious(self, session_id: str, content: str, reason: str) -> None:
        """Log suspicious input for security review."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id[:8] if len(session_id) >= 8 else session_id,
            "content_length": len(content),
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "reason": reason
        }
        
        try:
            with open(self.security_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except (IOError, OSError) as e:
            print(f"Warning: Could not log security violation: {e}")
