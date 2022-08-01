import logging

from machine_v2.models.core import Manual, HumanHelp
from machine_v2.plugins.base import MachineBasePlugin, Message
from machine_v2.plugins.decorators import respond_to

logger = logging.getLogger(__name__)


class HelpPlugin(MachineBasePlugin):
    """Getting Help"""

    @respond_to(r"^help$")
    async def help(self, msg: Message):
        """help: display this help text"""
        manual: Manual = await self.storage.get("manual", shared=True)
        help_text = "This is what I can respond to:\n\n"
        help_text += "\n\n".join([self._gen_class_help_text(cls, fns) for cls, fns in manual.human.items() if fns])
        await msg.say(help_text)

    @respond_to(r"^robot help$")
    async def robot_help(self, msg: Message):
        """robot help: display regular expressions that the bot responds to"""
        manual: Manual = await self.storage.get("manual", shared=True)
        help_text = "This is what triggers me:\n\n"
        help_text += "\n\n".join([self._gen_class_robot_help(cls, regexes) for cls, regexes in manual.robot.items()])
        await msg.say(help_text)

    def _gen_class_help_text(self, class_help: str, fn_helps: dict[str, HumanHelp]):
        help_text = "*{}:*\n".format(class_help)
        fn_help_texts = "\n".join([self._gen_help_text(fn_help) for fn_help in fn_helps.values()])
        help_text += fn_help_texts
        return help_text

    def _gen_help_text(self, fn_help: HumanHelp):
        return "\t*{}:* {}".format(fn_help.command, fn_help.help)

    def _gen_class_robot_help(self, class_help, regexes):
        help_text = "*{}:*\n".format(class_help)
        regex_helps = "\n".join([self._gen_bot_regex(regex) for regex in regexes])
        help_text += regex_helps
        return help_text

    def _gen_bot_regex(self, regex):
        bot_name = self.bot_info["name"]
        return "\t`{}`".format(regex.replace("@botname", "@" + bot_name))
