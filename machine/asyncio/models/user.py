from dataclasses import dataclass
from typing import Optional, Dict, Any

from dacite import from_dict


@dataclass(frozen=True)
class Profile:
    avatar_hash: str
    status_text: Optional[str]
    status_emoji: Optional[str]
    status_expiration: Optional[int]
    real_name: str
    display_name: str
    real_name_normalized: str
    display_name_normalized: str
    image_24: Optional[str]
    image_32: Optional[str]
    image_48: Optional[str]
    image_72: Optional[str]
    image_192: Optional[str]
    image_512: Optional[str]
    team: str
    email: Optional[str] = None
    image_original: Optional[str] = None


@dataclass(frozen=True)
class User:
    """
    User model that represents a user object from the Slack API
    """

    id: str
    team_id: Optional[str]
    name: str
    deleted: Optional[bool]
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

    @staticmethod
    def from_api_response(user_reponse: Dict[str, Any]) -> "User":
        return from_dict(data_class=User, data=user_reponse)  # pragma: no cover

    def fmt_mention(self) -> str:
        return f"<@{self.id}>"
