from __future__ import annotations
import logging
import random

import httpx
from slack_sdk.models.blocks import Block, ImageBlock, PlainTextObject

from machine.plugins.base import MachineBasePlugin, Message
from machine.plugins.decorators import respond_to, required_settings

logger = logging.getLogger(__name__)


def _make_blocks(search_string: str, image_url: str) -> list[Block]:
    blocks: list[Block] = [
        ImageBlock(image_url=image_url, alt_text=search_string, title=PlainTextObject(text=search_string))
    ]
    return blocks


@required_settings(["GOOGLE_CSE_ID", "GOOGLE_API_KEY"])
class ImageSearchPlugin(MachineBasePlugin):
    """Images"""

    @respond_to(r"(?:image|img)(?: me)? (?P<query>.+)")
    async def image_me(self, msg: Message, query: str) -> None:
        """image/img (me) <query>: find a random image"""
        results = await self._search(query.strip())
        if results:
            url = random.choice(results)
            await msg.say(blocks=_make_blocks(query, url))
        else:
            await msg.say(f"Couldn't find any results for '{query}'! :cry:")

    @respond_to(r"animate(?: me)? (?P<query>.+)")
    async def animate_me(self, msg: Message, query: str) -> None:
        """animate (me) <query>: find a random gif"""
        results = await self._search(query.strip(), animated=True)
        if results:
            url = random.choice(results)
            await msg.say(blocks=_make_blocks(query, url))
        else:
            await msg.say(f"Couldn't find any results for '{query}'! :cry:")

    async def _search(self, query: str, animated: bool = False) -> list[str]:
        query_params = {
            "cx": self.settings["GOOGLE_CSE_ID"],
            "key": self.settings["GOOGLE_API_KEY"],
            "q": query,
            "searchType": "image",
            "fields": "items(link)",
            "safe": "high",
        }

        if animated:
            query_params.update({"fileType": "gif", "hq": "animated", "tbs": "itp:animated"})
        timeout = httpx.Timeout(10.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get("https://www.googleapis.com/customsearch/v1", params=query_params)
        if response.status_code == httpx.codes.OK:
            data = response.json()
            results = [result["link"] for result in data["items"] if "items" in data]
        else:
            logger.warning(
                "An error occurred while searching! Status code: %s, response: %s", response.status_code, response.text
            )
            results = []
        return results
