import requests
from machine_v2.plugins.base import MachineBasePlugin, Message
from machine_v2.plugins.decorators import respond_to
from machine_v2.plugins.builtin.fun.regexes import url_regex


class MemePlugin(MachineBasePlugin):
    """Images"""

    # TODO: upload image via Slack API instead of posting URL?
    @respond_to(r"meme (?P<meme>\S+) (?P<top>.+);(?P<bottom>.+)")
    async def meme(self, msg: Message, meme, top, bottom):
        """meme <meme template> <top text>;<bottom text>: generate a meme"""
        character_replacements = {"?": "~q", "&": "~p", "#": "~h", "/": "~s", "''": '"'}
        query_string = "?font={}".format(self._font)
        for original, replacement in character_replacements.items():
            top = top.replace(original, replacement)
            bottom = bottom.replace(original, replacement)
        match = url_regex.match(meme)
        if match:
            query_string += "&background=" + match.group("url")
            meme = "custom"
            path = f"{self._base_url}/images/{meme}/{top.strip()}/{bottom.strip()}.jpg{query_string}".replace(" ", "-")
            await msg.say(path)
        else:
            path = f"{self._base_url}/images/{meme}/{top.strip()}/{bottom.strip()}{query_string}".replace(" ", "-")
            await msg.say(path)

    @respond_to(r"list memes")
    async def list_memes(self, msg):
        """list memes: list all the available meme templates"""
        ephemeral = not msg.is_dm
        status, templates = self._memegen_api_request("/templates/")
        if 200 <= status < 400:
            message = "*You can choose from these memes:*\n\n" + "\n".join(
                [f"\t_{template['id']}_: '{template['name']}'" for template in templates]
            )
            await msg.say(message, ephemeral=ephemeral)
        else:
            await msg.say("It seems I cannot find the memes you're looking for :cry:", ephemeral=ephemeral)

    def _memegen_api_request(self, path):
        url = self._base_url + path.lower()
        # TODO: replace requests with httpx
        r = requests.get(url)
        if r.ok:
            return r.status_code, r.json()
        else:
            return r.status_code, None

    @property
    def _base_url(self):
        return self.settings.get("MEMEGEN_URL", "https://api.memegen.link")

    @property
    def _font(self):
        return self.settings.get("MEMEGEN_FONT", "impact")