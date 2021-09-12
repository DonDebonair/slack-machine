from dataclasses import dataclass, field
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
    is_channel: Optional[bool]
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
    _members: List[str] = field(default_factory=list)

    @property
    def identifier(self):
        if self.name:
            return self.name
        else:
            return self.id

    @property
    def members(self) -> Optional[List[str]]:
        """Get the member IDs for the given users."""
        if not self._members:
            self._load_members()
        return self._members

    def _load_members(self):
        """Load a fresh set of members."""
        from machine.clients.singletons.slack import LowLevelSlackClient, call_paginated_endpoint
        web_client = LowLevelSlackClient.get_instance().web_client
        all_members = call_paginated_endpoint(
            web_client.conversations_members, 'members', channel=self.id
        )
        self._members.clear()
        for member in all_members:
            self._members.append(member)

    @staticmethod
    def from_api_response(user_reponse: Dict[str, Any]) -> 'Channel':
        return from_dict(data_class=Channel, data=user_reponse)
