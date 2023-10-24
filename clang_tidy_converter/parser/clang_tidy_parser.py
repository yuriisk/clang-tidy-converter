#!/usr/bin/env python3

from enum import Enum
import re

class ClangMessage:
    class Level(Enum):
        UNKNOWN = 0
        NOTE = 1
        REMARK = 2
        WARNING = 3
        ERROR = 4
        FATAL = 5

    def __init__(self, filepath=None, line=-1, column=-1, level=Level.UNKNOWN, message=None, diagnostic_name=None, details_lines=None, children=None):
        self.filepath = filepath if filepath is not None else ''
        self.line = line
        self.column = column
        self.level = level
        self.message = message if message is not None else ''
        self.diagnostic_name = diagnostic_name if diagnostic_name is not None else ''
        self.details_lines = details_lines if details_lines is not None else []
        self.children = children if children is not None else []

    @staticmethod
    def levelFromString(levelString):
        if levelString == 'note':
            return ClangMessage.Level.NOTE
        if levelString == 'remark':
            return ClangMessage.Level.REMARK
        if levelString == 'warning':
            return ClangMessage.Level.WARNING
        if levelString == 'error':
            return ClangMessage.Level.ERROR
        if levelString == 'fatal':
            return ClangMessage.Level.FATAL
        return ClangMessage.Level.UNKNOWN

class ClangTidyParser:
    MESSAGE_REGEX = re.compile(r"^(?P<filepath>.+):(?P<line>\d+):(?P<column>\d+): (?P<level>\S+): (?P<message>.*?)( \[(?P<diagnostic_name>.*)\])?$")
    IGNORE_REGEX = re.compile(r"^error:.*$")

    def __init__(self):
        pass

    def parse(self, lines):
        messages = []
        for line in lines:
            if self._is_ignored(line):
                continue
            message = self._parse_message(line)
            if message is None or message.level == ClangMessage.Level.UNKNOWN:
                if messages:
                    messages[-1].details_lines.append(line)
                else:
                    continue
            else:
                messages.append(message)
        return self._group_messages(messages)

    def _parse_message(self, line):
        regex_res = self.MESSAGE_REGEX.match(line)
        if regex_res is not None:
            return ClangMessage(
                        filepath=regex_res.group('filepath'),
                        line=int(regex_res.group('line')),
                        column=int(regex_res.group('column')),
                        level=ClangMessage.levelFromString(regex_res.group('level')),
                        message=regex_res.group('message'),
                        diagnostic_name=regex_res.group('diagnostic_name')
                   )
        return None

    def _is_ignored(self, line):
        return self.IGNORE_REGEX.match(line) is not None

    def _group_messages(self, messages):
        groupped_messages = []
        for msg in messages:
            if msg.level == ClangMessage.Level.NOTE:
                groupped_messages[-1].children.append(msg)
            else:
                groupped_messages.append(msg)
        return groupped_messages
