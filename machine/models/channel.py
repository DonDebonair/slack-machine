from typing import List, Optional

from pydantic import BaseModel


class PurposeTopic(BaseModel):
    value: str
    creator: Optional[str]
    last_set: int

    class Config:
        allow_mutation = False


class Channel(BaseModel):
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

    class Config:
        allow_mutation = False
