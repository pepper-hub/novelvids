"""DTOs for dashboard data."""

from pydantic import BaseModel

from novelvids.application.dto import NovelResponseDTO, UsageSummaryDTO


class DashboardStatsDTO(BaseModel):
    """DTO for dashboard statistics."""

    total_novels: int
    total_videos: int
    processing_time: float  # In hours
    balance: float
    recent_novels: list[NovelResponseDTO]
