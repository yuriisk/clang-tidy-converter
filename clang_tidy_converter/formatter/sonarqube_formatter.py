#!/usr/bin/env python3

import json

from ..parser import ClangMessage


class SonarQubeFormatter:
    """
    The JSON format used to import external issues into SonarQube
    https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/importing-external-issues/generic-issue-import-format/
    """

    def format(self, messages, args):
        return json.dumps({"issues": [self._format_message(msg, args) for msg in messages]}, indent=2)

    def _format_message(self, message: ClangMessage, args):
        return {
            "engineId": "clang-tidy",  # String
            "ruleId": message.diagnostic_name,  # String
            "primaryLocation": self._format_location(message, args),  # Location object
            "type": "CODE_SMELL",  # String. One of BUG, VULNERABILITY, CODE_SMELL
            "severity": self._level_to_severity(message.level),  # String. One of BLOCKER, CRITICAL, MAJOR, MINOR, INFO
            # "effortMinutes": "", # Integer, optional. Defaults to 0
            "secondaryLocations": [self._format_location(msg, args) for msg in message.children],  # Array of Location objects, optional
            # "_details": message.details_lines
        }

    def _format_location(self, message, args):
        range = {
            "startLine": message.line,
            "endLine": message.line,
        }
        if message.column > 0:
            range["startColumn"] = message.column - 1
            range["endColumn"] = message.column
        else:
            range["startColumn"] = 0
            range["endColumn"] = 1
        return {
            "message": message.message,
            "filePath": message.filepath,
            "textRange": range,
        }

    def _level_to_severity(self, level, default="BLOCKER"):
        return {
            ClangMessage.Level.NOTE: "INFO",
            ClangMessage.Level.REMARK: "MINOR",
            ClangMessage.Level.WARNING: "MAJOR",
            ClangMessage.Level.ERROR: "CRITICAL",
            ClangMessage.Level.FATAL: "BLOCKER",
        }.get(level, default)
