import requests
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import respond_to


class MemePlugin(MachineBasePlugin):
    """Images"""

    @respond_to(r'meme (?P<meme>\w+) (?P<top>.+);(?P<bottom>.+)')
    def meme(self, msg, meme, top, bottom):
        """meme <meme template> <top text>;<bottom text>: generate a meme"""
        character_replacements = {
            '?': '~q',
            '&': '~p',
            '#': '~h',
            '/': '~s',
            "''": '"'
        }
        for original, replacement in character_replacements.items():
            top = top.replace(original, replacement)
            bottom = bottom.replace(original, replacement)
        path = '/{}/{}/{}'.format(meme, top.strip(), bottom.strip()).replace(' ', '-')
        status, meme_info = self._memegen_request(path)
        if 200 <= status < 400:
            query_string = '?font=impact'
            msg.say(meme_info['direct']['visible'] + query_string)
        elif status == 404:
            msg.say("I don't know that meme. Use `list memes` to see what memes I have available")
        else:
            msg.say("Ooooops! Something went wrong :cry:")

    @respond_to(r'list memes')
    def list_memes(self, msg):
        """list memes: list all the available meme templates"""
        ephemeral = not msg.is_dm
        status, templates = self._memegen_request('/api/templates/')
        if 200 <= status < 400:
            message = "*You can choose from these memes:*\n\n" + "\n".join(
                ["\t_{}_: '{}'".format(url.rsplit('/', 1)[1], description) for description, url in
                 templates.items()]
            )
            msg.say_webapi(message, ephemeral=ephemeral)
        else:
            msg.say_webapi("It seems I cannot find the memes you're looking for :cry:",
                           ephemeral=ephemeral)

    def _memegen_request(self, path, query_params=None):
        base_url = self.settings.get('MEMEGEN_URL', 'https://memegen.link')
        url = base_url + path.lower()
        r = requests.get(url, params=query_params)
        if r.ok:
            return r.status_code, r.json()
        else:
            return r.status_code, None
