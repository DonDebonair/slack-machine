import random
import requests
import logging
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import respond_to, required_settings

logger = logging.getLogger(__name__)


@required_settings(['GOOGLE_CSE_ID', 'GOOGLE_API_KEY'])
class ImageSearchPlugin(MachineBasePlugin):
    """Images"""

    @respond_to(r'(?:image|img)(?: me)? (?P<query>.+)')
    def image_me(self, msg, query):
        """image/img (me) <query>: find a random image"""
        results = self._search(query.strip())
        if results:
            url = random.choice(results)
            msg.say(url)
        else:
            msg.say("Couldn't find any results for ''! :cry:".format(query))

    @respond_to(r'animate(?: me)? (?P<query>.+)')
    def animate_me(self, msg, query):
        """animate (me) <query>: find a random gif"""
        results = self._search(query.strip(), animated=True)
        if results:
            url = random.choice(results)
            msg.say(url)
        else:
            msg.say("Couldn't find any results for ''! :cry:".format(query))

    def _search(self, query, animated=False):
        query_params = {
            'cx': self.settings['GOOGLE_CSE_ID'],
            'key': self.settings['GOOGLE_API_KEY'],
            'q': query,
            'searchType': 'image',
            'fields': 'items(link)',
            'safe': 'high'
        }

        if animated:
            query_params.update({
                'fileType': 'gif',
                'hq': 'animated',
                'tbs': 'itp:animated'
            })
        r = requests.get('https://www.googleapis.com/customsearch/v1', params=query_params)
        if r.ok:
            response = r.json()
            results = [result["link"] for result in response["items"] if "items" in response]
        else:
            logger.warning("An error occurred while searching! Status code: %s, response: %s" % (
                r.status_code, r.text
            ))
            results = []
        return results
