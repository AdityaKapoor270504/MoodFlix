"""Pydantic schemas: the contract between the LLM and the rest of the code."""
from pydantic import BaseModel, Field


class MoodProfile(BaseModel):
    current_emotions: list[str] = Field(default_factory=list)
    desired_feeling: str = ""
    desired_mood_tags: list[str] = Field(default_factory=list)
    preferred_genres: list[str] = Field(default_factory=list)
    avoid_genres: list[str] = Field(default_factory=list)
    pacing: str = "any"
    max_runtime_minutes: int = 0  # 0 means no limit
    summary: str = ""


class Recommendation(BaseModel):
    title: str
    match_score: int = Field(ge=1, le=10)
    reason: str
    plot: str = ""  # spoiler-free premise written by the LLM


class RerankResult(BaseModel):
    recommendations: list[Recommendation]
