#!/usr/bin/env python3

import sys
from typing import List, Dict, Callable, Union, NewType
from pathlib import Path
import json


class SlackMsg:
    def __init__(self, user: str, message: str):
        self.user = user
        self.message = message

    def __str__(self):
        return self.message

    @classmethod
    def from_exported(cls, response: Dict[str, Union[str, Dict[str, str]]]) -> 'SlackMsg':
        return SlackMsg(
            response.get("user_profile", {}).get("display_name", ""),
            response.get("text"),
        )

    @classmethod
    def from_exported_list(cls, responses: List[Dict[str, Union[str, Dict[str, str]]]]) -> List['SlackMsg']:
        return [SlackMsg.from_exported(response) for response in responses]


SlackMsgFilter = NewType('SlackMsgFilter', Callable[[SlackMsg], bool])


def only_link_filter() -> SlackMsgFilter:
    return lambda msg: not msg.message.startswith("<http")


def user_filter(display_name: str) -> SlackMsgFilter:
    return lambda msg: msg.user == display_name


def and_filter(*filters: SlackMsgFilter) -> SlackMsgFilter:
    def result(msg: SlackMsg) -> bool:
        for msg_filter in filters:
            if not msg_filter(msg):
                return False
        return True
    return result


def load_jsons(file_paths: List[Path]) -> List[SlackMsg]:
    result: List[SlackMsg] = []

    for file_path in file_paths:
        with file_path.open("r") as f:
            responses = json.load(f)
            result.extend(SlackMsg.from_exported_list(responses))

    return result


def main(args: List[str]):
    display_name = args[0]
    file_paths = [Path(arg) for arg in args[1:]]

    messages = load_jsons(file_paths)
    msg_filter = and_filter(user_filter(display_name), only_link_filter())
    filtered = filter(msg_filter, messages)

    for msg in filtered:
        print(msg)


if __name__ == "__main__":
    main(sys.argv[1:])
