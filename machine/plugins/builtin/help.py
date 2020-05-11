# -*- coding: utf-8 -*-

from typing import List, Optional

from machine.message import Message
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import respond_to


class HelpPlugin(MachineBasePlugin):
    """Getting Help"""

    @respond_to(r"^help(?:\s+?(?P<topic>\w+)?)?")
    async def help(self, msg: Message, topic: Optional[str]):
        """ help [topic]: display this help text or display the manual for a topic/command
        """

        manual = (await self.storage.get("manual", shared=True))["human"]
        print(f"Topic {topic}")
        if not topic:
            help_text = self._gen_manual_overview(manual)
        else:
            help_text = self._gen_topic_overview(manual, topic)

        await msg.reply(help_text, ephemeral=True)

    @respond_to(r"^robot help$")
    async def robot_help(self, msg: Message):
        """ robot help: display regular expressions that the bot responds to
        """
        robot_manual = (await self.storage.get("manual", shared=True))["robot"]
        help_text = "This is what triggers me:\n\n"
        help_text += "\n\n".join(
            [
                self._gen_class_robot_help(cls, regexes)
                for cls, regexes in robot_manual.items()
            ]
        )
        await msg.reply(help_text, ephemeral=True)

    def _gen_manual_overview(self, manual: dict) -> str:
        help_text = "This is what I can respond to:\n\n"
        help_text += "\n\n".join(
            [self._gen_class_help_text(cls, fns) for cls, fns in manual.items() if fns]
        )
        return help_text

    def _gen_topic_overview(self, manual: dict, topic: str) -> str:
        help_text = ""
        for cls, fns in manual.items():
            cls = cls.strip()
            if not fns:
                continue

            for _, fn_help in fns.items():
                command = fn_help["command"].lower().strip()
                if topic.lower().strip() != command:
                    continue

                help_text += f"Manual for *{topic}* (from *{cls}*):\n\n"
                help_text += self._gen_long_help_text(fn_help)
                help_text += "\n"

        return help_text or f"Topic `{topic}` not found in manual."

    def _gen_class_help_text(self, class_help: str, fn_helps: dict) -> str:
        help_text = "*{}:*\n".format(class_help)
        fn_help_texts = "\n".join(
            [self._gen_short_help_text(fn_help) for fn_help in fn_helps.values()]
        )
        help_text += fn_help_texts
        return help_text

    def _gen_short_help_text(self, fn_help: dict) -> str:
        command = fn_help["command"]
        summary = fn_help["summary"]
        return f"\t*{command}*: {summary}"

    def _gen_long_help_text(self, fn_help: dict) -> str:
        short = self._gen_short_help_text(fn_help)
        desc = fn_help["description"]
        if not desc:
            return short

        desc = "\n".join([f"\t\t{line}" for line in desc])
        return f"{short}\n{desc}"

    def _gen_class_robot_help(self, class_help: str, regexes: List[str]) -> str:
        help_text = "*{}:*\n".format(class_help)
        regex_helps = "\n".join([self._gen_bot_regex(regex) for regex in regexes])
        help_text += regex_helps
        return help_text

    def _gen_bot_regex(self, regex: str) -> str:
        bot_name = self.retrieve_bot_info()["name"]
        return "\t`{}`".format(regex.replace("@botname", "@" + bot_name))
