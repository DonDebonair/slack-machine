import logging
from typing import Any

from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import process

logger = logging.getLogger(__name__)


class EchoPlugin(MachineBasePlugin):
    @process(slack_event_type="message")
    async def echo_message(self, event: dict[str, Any]) -> None:
        logger.debug("Message received: %s", event)
        if (
            "subtype" in event and (event["subtype"] == "bot_message" or event["subtype"] == "message_replied")
        ) or event["user"] == self.bot_info["user_id"]:
            return
        if "thread_ts" in event:
            thread_ts = event["thread_ts"]
        else:
            thread_ts = None
        await self.say(event["channel"], event["text"], thread_ts=thread_ts)
