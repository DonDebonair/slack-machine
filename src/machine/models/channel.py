from typing import Optional

from pydantic import BaseModel, ConfigDict


class PurposeTopic(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: str
    creator: Optional[str] = None
    last_set: int


class Channel(BaseModel):
    """Channel model that represents a channel object from the Slack API"""

    model_config = ConfigDict(frozen=True)

    id: str
    name: Optional[str] = None
    created: int
    creator: Optional[str] = None
    is_archived: bool
    is_general: Optional[bool] = None
    name_normalized: Optional[str] = None
    is_shared: Optional[bool] = None
    is_org_shared: bool
    is_member: Optional[bool] = None
    is_private: Optional[bool] = None
    is_mpim: Optional[bool] = None
    is_channel: Optional[bool] = None
    is_group: Optional[bool] = None
    is_im: Optional[bool] = None
    user: Optional[str] = None
    topic: Optional[PurposeTopic] = None
    purpose: Optional[PurposeTopic] = None
    previous_names: Optional[list[str]] = None

    @property
    def identifier(self) -> str:
        """Return the name of the channel if it exists, otherwise return the id"""
        if self.name:
            return self.name
        else:
            return self.id
