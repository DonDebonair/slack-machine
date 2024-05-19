import copy
import json
import sys
from types import MethodType
from typing import Optional, Union

from slack_sdk.models import JsonObject
from slack_sdk.models.blocks import (
    Block,
    BlockElement,
    MarkdownTextObject,
    Option,
    PlainTextObject,
    TextObject,
)
from slack_sdk.models.views import View


def repr_override(self):
    values_dict = self.__dict__
    if values_dict:
        non_null_values_dict = {k: v for k, v in values_dict.items() if v is not None}
        only_public_values_dict = {k: v for k, v in non_null_values_dict.items() if not k.startswith("_")}
        type_removed_dict = {k: v for k, v in only_public_values_dict.items() if k != "type"}
        args_string = ", ".join([f"{k}={repr(v)}" for k, v in type_removed_dict.items()])
        return f"{self.__class__.__name__}({args_string})"
    else:
        return self.__str__()


def parse(cls, block_element: Union[dict, "BlockElement"]) -> Optional[Union["BlockElement", TextObject]]:
    if block_element is None:  # skipcq: PYL-R1705
        return None
    elif isinstance(block_element, dict):
        if "type" in block_element:
            d = copy.copy(block_element)
            t = d.pop("type")
            for subclass in cls._get_sub_block_elements():
                if t == subclass.type:  # type: ignore
                    if "options" in d:
                        d["options"] = Option.parse_all(d["options"])
                    return subclass(**d)
            if t == PlainTextObject.type:  # skipcq: PYL-R1705
                return PlainTextObject(**d)
            elif t == MarkdownTextObject.type:
                return MarkdownTextObject(**d)
    elif isinstance(block_element, (TextObject, BlockElement)):
        return block_element
    cls.logger.warning(f"Unknown element detected and skipped ({block_element})")
    return None


def main():
    View.__repr__ = repr_override
    JsonObject.__repr__ = repr_override
    BlockElement.parse = MethodType(parse, BlockElement)
    input_file_path = sys.argv[1]
    with open(input_file_path) as f:
        d = json.load(f)
        blocks = Block.parse_all(d["blocks"])
        if "type" in d and (d["type"] == "modal" or d["type"] == "home"):
            if d["type"] == "modal":
                view = View(type="modal", title=d["title"], submit=d["submit"], close=d["close"], blocks=blocks)
            elif d["type"] == "home":
                view = View(type="home", blocks=blocks)
            print(repr(view))
        else:
            print(repr(blocks))


if __name__ == "__main__":
    main()
