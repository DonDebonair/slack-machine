from __future__ import annotations
from typing import Tuple, Any

import httpx
from slack_sdk.models.blocks import ImageBlock, PlainTextObject

from machine.plugins.base import MachineBasePlugin, Message
from machine.plugins.decorators import respond_to
from machine.plugins.builtin.fun.regexes import url_regex


class MemePlugin(MachineBasePlugin):
    """Images"""

    @respond_to(r"meme (?P<meme>\S+) (?P<top>.+);(?P<bottom>.+)")
    async def meme(self, msg: Message, meme: str, top: str, bottom: str) -> None:
        """meme <meme template> <top text>;<bottom text>: generate a meme"""
        character_replacements = {"?": "~q", "&": "~p", "#": "~h", "/": "~s", "''": '"'}
        query_string = f"?font={self._font}"
        for original, replacement in character_replacements.items():
            top = top.replace(original, replacement)
            bottom = bottom.replace(original, replacement)
        match = url_regex.match(meme)
        if match:
            query_string += "&background=" + match.group("url")
            meme = "custom"
            path = f"{self._base_url}/images/{meme}/{top.strip()}/{bottom.strip()}.jpg{query_string}".replace(" ", "-")
        else:
            path = f"{self._base_url}/images/{meme}/{top.strip()}/{bottom.strip()}{query_string}".replace(" ", "-")
        title = f"{top.strip()} - {bottom.strip()}"
        blocks = [ImageBlock(image_url=path, alt_text=title, title=PlainTextObject(text=title))]
        await msg.say(blocks=blocks)

    @respond_to(r"list memes")
    async def list_memes(self, msg: Message) -> None:
        """list memes: list all the available meme templates"""
        ephemeral = not msg.is_dm
        status, templates = await self._memegen_api_request("/templates/")
        if 200 <= status < 400 and templates is not None:
            message = "*You can choose from these memes:*\n\n" + "\n".join(
                [f"\t_{template['id']}_: '{template['name']}'" for template in templates]
            )
            await msg.say(message, ephemeral=ephemeral)
        else:
            await msg.say("It seems I cannot find the memes you're looking for :cry:", ephemeral=ephemeral)

    async def _memegen_api_request(self, path: str) -> Tuple[int, list[dict[str, Any]] | None]:
        url = self._base_url + path.lower()
        timeout = httpx.Timeout(10.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
        if response.status_code == httpx.codes.OK:
            return response.status_code, response.json()
        else:
            return response.status_code, None

    @property
    def _base_url(self) -> str:
        return self.settings.get("MEMEGEN_URL", "https://api.memegen.link")

    @property
    def _font(self) -> str:
        return self.settings.get("MEMEGEN_FONT", "impact")
