from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from dacite import from_dict


@dataclass(frozen=True)
class PurposeTopic:
    value: str
    creator: Optional[str]
    last_set: int


@dataclass(frozen=True)
class Channel:
    """
    Channel model that represents a channel object from the Slack API
    """

    id: str
    name: Optional[str]
    created: int
    creator: Optional[str]
    is_archived: bool
    is_general: Optional[bool]
    name_normalized: Optional[str]
    is_shared: Optional[bool]
    is_org_shared: bool
    is_member: Optional[bool]
    is_private: Optional[bool]
    is_mpim: Optional[bool]
    is_channel: Optional[bool]
    is_group: Optional[bool]
    is_im: Optional[bool]
    user: Optional[str]
    topic: Optional[PurposeTopic]
    purpose: Optional[PurposeTopic]
    previous_names: Optional[List[str]]

    @property
    def identifier(self) -> str:
        if self.name:
            return self.name
        else:
            return self.id

    @staticmethod
    def from_api_response(user_reponse: Dict[str, Any]) -> "Channel":
        return from_dict(data_class=Channel, data=user_reponse)
