from typing import Optional

from pydantic import BaseModel, ConfigDict


class Profile(BaseModel):
    model_config = ConfigDict(frozen=True)

    avatar_hash: str
    status_text: Optional[str] = None
    status_emoji: Optional[str] = None
    status_expiration: Optional[int] = None
    real_name: str
    display_name: str
    real_name_normalized: str
    display_name_normalized: str
    image_24: Optional[str] = None
    image_32: Optional[str] = None
    image_48: Optional[str] = None
    image_72: Optional[str] = None
    image_192: Optional[str] = None
    image_512: Optional[str] = None
    team: str
    email: Optional[str] = None
    image_original: Optional[str] = None


class User(BaseModel):
    """User model that represents a user object from the Slack API"""

    model_config = ConfigDict(frozen=True)

    id: str
    team_id: Optional[str] = None
    name: str
    deleted: Optional[bool] = None
    profile: Profile
    is_bot: bool
    updated: int
    is_app_user: bool
    color: Optional[str] = None
    real_name: Optional[str] = None
    tz: Optional[str] = None
    tz_label: Optional[str] = None
    tz_offset: Optional[int] = None
    is_admin: Optional[bool] = None
    is_owner: Optional[bool] = None
    is_primary_owner: Optional[bool] = None
    is_restricted: Optional[bool] = None
    is_ultra_restricted: Optional[bool] = None
    is_stranger: Optional[bool] = None
    has_2fa: Optional[bool] = None
    locale: Optional[str] = None

    def fmt_mention(self) -> str:
        """Format the user as a mention"""
        return f"<@{self.id}>"
