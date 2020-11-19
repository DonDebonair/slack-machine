from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union

from dacite import from_dict, Config


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
    name: Optional[str]
    is_channel: Optional[bool]
    created: int
    creator: Union[str, None]
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
    members: Optional[List[str]]
    topic: Optional[PurposeTopic]
    purpose: Optional[PurposeTopic]
    previous_names: Optional[List[str]]

    @property
    def identifier(self):
        if self.name:
            return self.name
        else:
            return self.id

    @staticmethod
    def from_api_response(user_reponse: Dict[str, Any]) -> 'Channel':
        config = Config()
        config.check_types = False
        return from_dict(data_class=Channel, data=user_reponse, config=config)
