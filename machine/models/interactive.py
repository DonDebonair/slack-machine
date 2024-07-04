from __future__ import annotations

from datetime import date, time
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, TypeAdapter
from pydantic.functional_validators import PlainValidator, model_validator
from pydantic_core.core_schema import ValidationInfo
from slack_sdk.models.blocks import Block as SlackSDKBlock
from typing_extensions import Annotated


class TypedModel(BaseModel):
    type: str


class User(BaseModel):
    id: str
    username: str
    name: str
    team_id: str


class Team(BaseModel):
    id: str
    domain: str


class Channel(BaseModel):
    id: str
    name: str


class MessageContainer(TypedModel):
    type: Literal["message"]
    message_ts: str
    channel_id: str
    is_ephemeral: bool


class MessageAttachmentContainer(TypedModel):
    type: Literal["message_attachment"]
    message_ts: str
    attachment_id: int
    channel_id: str
    is_ephemeral: bool
    is_app_unfurl: bool


class ViewContainer(TypedModel):
    type: Literal["view"]
    view_id: str


Container = Annotated[Union[MessageContainer, MessageAttachmentContainer, ViewContainer], Field(discriminator="type")]


class PlainText(TypedModel):
    type: Literal["plain_text"]
    text: str
    emoji: bool


class MarkdownText(TypedModel):
    type: Literal["mrkdwn"]
    text: str
    verbatim: bool


Text = Annotated[Union[PlainText, MarkdownText], Field(discriminator="type")]


class Option(BaseModel):
    text: Text
    value: str


class CheckboxValues(TypedModel):
    type: Literal["checkboxes"]
    selected_options: List[Option]


class DatepickerValue(TypedModel):
    type: Literal["datepicker"]
    selected_date: Optional[date]


class EmailValue(TypedModel):
    type: Literal["email_text_input"]
    value: Optional[str] = None


class StaticSelectValue(TypedModel):
    type: Literal["static_select"]
    selected_option: Optional[Option]


class ChannelSelectValue(TypedModel):
    type: Literal["channels_select"]
    selected_channel: Optional[str]


class ConversationSelectValue(TypedModel):
    type: Literal["conversations_select"]
    selected_conversation: Optional[str]


class UserSelectValue(TypedModel):
    type: Literal["users_select"]
    selected_user: Optional[str]


class ExternalSelectValue(TypedModel):
    type: Literal["external_select"]
    selected_option: Optional[str]


class MultiStaticSelectValues(TypedModel):
    type: Literal["multi_static_select"]
    selected_options: List[Option]


class MultiChannelSelectValues(TypedModel):
    type: Literal["multi_channels_select"]
    selected_channels: List[str]


class MultiConversationSelectValues(TypedModel):
    type: Literal["multi_conversations_select"]
    selected_conversations: List[str]


class MultiUserSelectValues(TypedModel):
    type: Literal["multi_users_select"]
    selected_users: List[str]


class MultiExternalSelectValues(TypedModel):
    type: Literal["multi_external_select"]
    selected_options: List[str]


class NumberValue(TypedModel):
    type: Literal["number_input"]
    value: Union[float, int, None] = None


class PlainTextInputValue(BaseModel):
    type: Literal["plain_text_input"]
    value: Optional[str]


class RichTextInputValue(TypedModel):
    type: Literal["rich_text_input"]
    value: Optional[str]


class RadioValues(TypedModel):
    type: Literal["radio_buttons"]
    selected_option: Optional[Option]


class TimepickerValue(TypedModel):
    type: Literal["timepicker"]
    selected_time: Optional[time]


class UrlValue(TypedModel):
    type: Literal["url_text_input"]
    value: Optional[str] = None


Values = Annotated[
    Union[
        CheckboxValues,
        DatepickerValue,
        EmailValue,
        StaticSelectValue,
        ChannelSelectValue,
        ConversationSelectValue,
        UserSelectValue,
        ExternalSelectValue,
        MultiStaticSelectValues,
        MultiChannelSelectValues,
        MultiConversationSelectValues,
        MultiUserSelectValues,
        MultiExternalSelectValues,
        NumberValue,
        PlainTextInputValue,
        RichTextInputValue,
        RadioValues,
        TimepickerValue,
        UrlValue,
    ],
    Field(discriminator="type"),
]


class State(BaseModel):
    values: Dict[str, Dict[str, Values]]


class BaseAction(TypedModel):
    action_id: str
    block_id: str
    type: str
    action_ts: str


class RadioButtonsAction(BaseAction):
    type: Literal["radio_buttons"]
    selected_option: Option


class ButtonAction(BaseAction):
    type: Literal["button"]
    text: Text
    value: Optional[str] = None
    style: Optional[str] = None


class CheckboxAction(BaseAction):
    type: Literal["checkboxes"]
    selected_options: List[Option]


class DatepickerAction(BaseAction):
    type: Literal["datepicker"]
    selected_date: Optional[date]


class StaticSelectAction(BaseAction):
    type: Literal["static_select"]
    selected_option: Option


class ChannelSelectAction(BaseAction):
    type: Literal["channels_select"]
    selected_channel: str


class ConversationSelectAction(BaseAction):
    type: Literal["conversations_select"]
    selected_conversation: str


class UserSelectAction(BaseAction):
    type: Literal["users_select"]
    selected_user: str


class ExternalSelectAction(BaseAction):
    type: Literal["external_select"]
    selected_option: str


class MultiStaticSelectAction(BaseAction):
    type: Literal["multi_static_select"]
    selected_options: List[Option]


class MultiChannelSelectAction(BaseAction):
    type: Literal["multi_channels_select"]
    selected_channels: List[str]


class MultiConversationSelectAction(BaseAction):
    type: Literal["multi_conversations_select"]
    selected_conversations: List[str]


class MultiUserSelectAction(BaseAction):
    type: Literal["multi_users_select"]
    selected_users: List[str]


class MultiExternalSelectAction(BaseAction):
    type: Literal["multi_external_select"]
    selected_options: List[str]


class TimepickerAction(BaseAction):
    type: Literal["timepicker"]
    selected_time: time


class UrlAction(BaseAction):
    type: Literal["url_text_input"]
    value: str


class OverflowAction(BaseAction):
    type: Literal["overflow"]
    selected_option: Option


class PlainTextInputAction(BaseAction):
    type: Literal["plain_text_input"]
    value: str


class RichTextInputAction(BaseAction):
    type: Literal["rich_text_input"]
    value: str


Action = Annotated[
    Union[
        RadioButtonsAction,
        ButtonAction,
        CheckboxAction,
        DatepickerAction,
        StaticSelectAction,
        ChannelSelectAction,
        ConversationSelectAction,
        UserSelectAction,
        ExternalSelectAction,
        MultiStaticSelectAction,
        MultiChannelSelectAction,
        MultiConversationSelectAction,
        MultiUserSelectAction,
        MultiExternalSelectAction,
        TimepickerAction,
        UrlAction,
        OverflowAction,
        PlainTextInputAction,
        RichTextInputAction,
    ],
    Field(discriminator="type"),
]


def validate_block(block: Any, info: ValidationInfo) -> SlackSDKBlock:
    block = SlackSDKBlock.parse(block)
    if block is None:
        raise ValueError("Block was not recognized!")
    return block


Block = Annotated[SlackSDKBlock, PlainValidator(validate_block)]


class Message(BaseModel):
    user: str
    type: str
    ts: str
    bot_id: str
    app_id: str
    text: str
    team: str
    blocks: List[Block]


class View(BaseModel):
    id: str
    team_id: str
    type: Literal["modal", "home"]
    blocks: List[Block]
    private_metadata: str
    callback_id: str
    state: State
    hash: str
    title: Text
    clear_on_close: bool
    notify_on_close: bool
    close: Optional[Text]
    submit: Optional[Text]
    previous_view_id: Optional[str]
    root_view_id: str
    app_id: str
    external_id: str
    app_installed_team_id: str
    bot_id: str


class ResponseUrlForView(BaseModel):
    block_id: str
    action_id: str
    channel_id: str
    response_url: str


class BlockActionsPayload(TypedModel):
    type: Literal["block_actions"]
    user: User
    api_app_id: str
    token: str
    container: Container
    trigger_id: str
    team: Team
    enterprise: Optional[str]
    is_enterprise_install: bool
    channel: Optional[Channel] = None
    message: Optional[Message] = None
    view: Optional[View] = None
    state: Optional[State] = None
    response_url: Optional[str] = None
    actions: List[Action]

    @model_validator(mode="after")
    def validate_view_or_message(self) -> BlockActionsPayload:
        if self.view is None and self.message is None:
            raise ValueError("Either view or message must be present!")
        if self.message is not None:
            if self.channel is None:
                raise ValueError("channel must be present when message is present!")
            if self.state is None:
                raise ValueError("state must be present when message is present!")
            if self.response_url is None:
                raise ValueError("response_url must be present when message is present!")
        return self


class ViewSubmissionPayload(TypedModel):
    type: Literal["view_submission"]
    team: Team
    user: User
    view: View
    enterprise: Optional[str]
    api_app_id: str
    token: str
    trigger_id: str
    response_urls: List[ResponseUrlForView]
    is_enterprise_install: bool


InteractivePayload: TypeAdapter[Union[BlockActionsPayload, ViewSubmissionPayload]] = TypeAdapter(
    Annotated[Union[BlockActionsPayload, ViewSubmissionPayload], Field(discriminator="type")]
)
