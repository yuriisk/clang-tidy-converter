#!/usr/bin/env python3

import json

from ..parser import ClangMessage


class SarifFormatter:
    """
    Follows the SARIF format as used by SonarQube
    https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/importing-external-issues/importing-issues-from-sarif-reports/
    """

    def format(self, messages, args):
        return json.dumps({
            "version": "2.1.0",
            "runs": [{
                "tool": {"driver": {"name": "clang-tidy"}},
                "results": [self._format_message(msg, args) for msg in messages]
            }]
        }, indent=2)

    def _format_message(self, message: ClangMessage, args):
        return {
            "message": {"text": message.message},
            "ruleId": message.diagnostic_name,
            "locations": [self._format_location(msg, args) for msg in [
                message, *message.children]],
            "level": self._convert_level(message.level),
        }

    def _format_location(self, message, args):
        return {
            "message": message.message,
            "artifactLocation": {"uri": "file://" + message.filepath},
            "region": {
                "startLine": message.line,
                "startColumn": message.column,
            },
        }

    def _convert_level(self, level, default=""):
        return {
            ClangMessage.Level.NOTE: "none",
            ClangMessage.Level.REMARK: "note",
            ClangMessage.Level.WARNING: "warning",
            ClangMessage.Level.ERROR: "error",
            ClangMessage.Level.FATAL: "error",
        }.get(level, default)
