# -*- coding: utf-8 -*-

from aiohttp.client import ClientSession
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import respond_to
from machine.plugins.builtin.fun.regexes import url_regex


class MemePlugin(MachineBasePlugin):
    """Images"""

    @respond_to(r"meme (?P<meme>\S+) (?P<top>.+);(?P<bottom>.+)")
    async def meme(self, msg, meme, top, bottom):
        """meme <meme template> <top text>;<bottom text>: generate a meme"""
        character_replacements = {"?": "~q", "&": "~p", "#": "~h", "/": "~s", "''": '"'}
        query_string = "?font={}".format(self._font)
        for original, replacement in character_replacements.items():
            top = top.replace(original, replacement) if top else ""
            bottom = bottom.replace(original, replacement) if bottom else ""

        match = url_regex.match(meme)
        if match:
            query_string = query_string + "&alt=" + match.group("url")
            meme = "custom"
            path = "{}/{}/{}/{}.jpg{}".format(
                self._base_url, meme, top.strip(), bottom.strip(), query_string
            ).replace(" ", "-")
            await msg.say(path)
        else:
            path = "/{}/{}/{}".format(
                meme.strip(), top.strip(), bottom.strip()
            ).replace(" ", "-")
            status, meme_info = await self._memegen_api_request(path)
            if 200 <= status < 400:
                await msg.say(meme_info["direct"]["masked"] + query_string)
            elif status == 404:
                await msg.say(
                    "I don't know that meme. Use `list memes` to see what memes I have available"
                )
            else:
                await msg.say("Ooooops! Something went wrong :cry:")

    @respond_to(r"list (dank )?(memes|maymays)")
    async def list_memes(self, msg):
        """list memes: list all the available meme templates"""
        ephemeral = not msg.is_dm
        status, templates = await self._memegen_api_request("/api/templates/")
        if 200 <= status < 400:
            message = "*You can choose from these memes:*\n\n" + "\n".join(
                [
                    "\t_{}_: '{}'".format(url.rsplit("/", 1)[1], description)
                    for description, url in templates.items()
                ]
            )
            await msg.say(message, ephemeral=ephemeral)
        else:
            await msg.reply(
                "It seems I cannot find the memes you're looking for :cry:",
                in_thread=True,
            )

    async def _memegen_api_request(self, path):
        url = self._base_url + path.lower()
        async with ClientSession() as session:
            async with session.get(url) as resp:
                if resp.reason == "OK":
                    return resp.status, await resp.json()
                else:
                    return resp.status, None

    @property
    def _base_url(self):
        return self.settings.get("MEMEGEN_URL", "https://memegen.link")

    @property
    def _font(self):
        return self.settings.get("MEMEGEN_FONT", "impact")
