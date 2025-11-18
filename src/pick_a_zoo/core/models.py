"""Pydantic models for Pick-a-Zoo data structures."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, HttpUrl, field_validator


def validate_url(v: str | HttpUrl) -> HttpUrl:
    """Validate and convert string to HttpUrl."""
    if isinstance(v, HttpUrl):
        return v
    return HttpUrl(v)


class WindowSize(BaseModel):
    """Window dimensions for video playback."""

    width: int = Field(gt=0, description="Window width in pixels (must be > 0)")
    height: int = Field(gt=0, description="Window height in pixels (must be > 0)")


# Default window size for new feeds (1280x720 HD)
DEFAULT_WINDOW_SIZE = WindowSize(width=1280, height=720)


class Feed(BaseModel):
    """Represents a single camera feed entry."""

    name: str = Field(min_length=1, description="Feed name (required, non-empty)")
    url: Annotated[str | HttpUrl, BeforeValidator(validate_url)]
    window_size: WindowSize | None = None

    @field_validator("name")
    @classmethod
    def validate_name_stripped(cls, v: str) -> str:
        """Strip whitespace from feed name and ensure it's non-empty."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Feed name must be a non-empty string after stripping whitespace")
        return stripped

