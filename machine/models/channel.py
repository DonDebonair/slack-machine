from dataclasses import dataclass
from typing import List, Dict, Any

from dacite import from_dict


@dataclass(frozen=True)
class PurposeTopic:
    value: str
    creator: str
    last_set: int


@dataclass(frozen=True)
class Channel:
    """
    Channel model that represents a channel object from the Slack API
    """
    id: str
    name: str
    is_channel: bool
    created: int
    creator: str
    is_archived: bool
    is_general: bool
    name_normalized: str
    is_shared: bool
    is_org_shared: bool
    is_member: bool
    is_private: bool
    is_mpim: bool
    members: List[str]
    topic: PurposeTopic
    purpose: PurposeTopic
    previous_names: List[str]

    @staticmethod
    def from_api_response(user_reponse: Dict[str, Any]) -> 'Channel':
        return from_dict(data_class=Channel, data=user_reponse)
