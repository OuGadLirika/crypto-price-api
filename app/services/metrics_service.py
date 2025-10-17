from __future__ import annotations

import time
from typing import Dict, Any


class MetricsService:
    """
    Service for collecting and storing application metrics.
    
    Tracks:
    - Total requests
    - Total errors
    - Uptime
    - Success rate
    """
    
    def __init__(self) -> None:
        self._start_time = time.time()
        self._request_count = 0
        self._error_count = 0

    def increment_request_count(self) -> None:
        """Increment total request counter."""
        self._request_count += 1

    def increment_error_count(self) -> None:
        """Increment error counter."""
        self._error_count += 1

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics snapshot.
        
        Returns:
            Dictionary containing current metrics
        """
        uptime = int(time.time() - self._start_time)
        
        return {
            "uptime_seconds": uptime,
            "requests_total": self._request_count,
            "errors_total": self._error_count,
            "success_rate": (
                (self._request_count - self._error_count) / self._request_count * 100
                if self._request_count > 0
                else 100.0
            ),
        }
