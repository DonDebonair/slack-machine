from dataclasses import dataclass
from typing import Optional, Dict, Any

from dacite import from_dict


@dataclass(frozen=True)
class Profile:
    avatar_hash: str
    status_text: str
    status_emoji: str
    status_expiration: int
    real_name: str
    display_name: str
    real_name_normalized: str
    display_name_normalized: str
    email: Optional[str]
    image_original: Optional[str]
    image_24: str
    image_32: str
    image_48: str
    image_72: str
    image_192: str
    image_512: str
    team: str


@dataclass(frozen=True)
class User:
    """
    User model that represents a user object from the Slack API
    """
    id: str
    team_id: str
    name: str
    deleted: bool
    color: Optional[str]
    real_name: Optional[str]
    tz: Optional[str]
    tz_label: Optional[str]
    tz_offset: Optional[int]
    profile: Profile
    is_admin: Optional[bool]
    is_owner: Optional[bool]
    is_primary_owner: Optional[bool]
    is_restricted: Optional[bool]
    is_ultra_restricted: Optional[bool]
    is_bot: bool
    is_stranger: Optional[bool]
    updated: int
    is_app_user: bool
    has_2fa: Optional[bool]
    locale: Optional[str]

    @staticmethod
    def from_api_response(user_reponse: Dict[str, Any]) -> 'User':
        return from_dict(data_class=User, data=user_reponse)

    def fmt_mention(self) -> str:
        return "<@{}>".format(self.id)
