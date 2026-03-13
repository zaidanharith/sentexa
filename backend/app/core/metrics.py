from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class MetricsState:
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_requests: int = 0
    total_latency_ms: float = 0.0
    requests_by_status: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def record(self, status_code: int, latency_ms: float) -> None:
        self.total_requests += 1
        self.total_latency_ms += latency_ms
        self.requests_by_status[str(status_code)] += 1

    def snapshot(self) -> dict:
        avg_latency_ms = (
            self.total_latency_ms / self.total_requests if self.total_requests else 0.0
        )
        return {
            "started_at": self.started_at.isoformat(),
            "total_requests": self.total_requests,
            "requests_by_status": dict(self.requests_by_status),
            "avg_latency_ms": round(avg_latency_ms, 2),
        }

metrics_state = MetricsState()