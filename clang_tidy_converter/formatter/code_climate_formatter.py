#!/usr/bin/env python3

import json
import hashlib

from ..parser import ClangMessage

def remove_duplicates(l):
    return list(set(l))

class CodeClimateFormatter:
    def __init__(self):
        pass

    def format(self, messages, args):
        formatted_string = ""
        for message in messages:
            formatted_string += json.dumps(self._format_message(message, args), indent=2) + '\0\n'
        return formatted_string

    def _format_message(self, message, args):
        return {
            'type': 'issue',
            'check_name': message.diagnostic_name,
            'description': message.message,
            'content': self._extract_content(message, args),
            'categories': self._extract_categories(message, args),
            'location': self._extract_location(message, args),
            'trace': self._extract_trace(message, args),
            'severity': self._extract_severity(message, args),
            'fingerprint': self._generate_fingerprint(message)
        }

    def _extract_content(self, message, args):
        return {
            'body': '\n'.join(['```'] + message.details_lines + self._messages_to_text(message.children) + ['```'])
        }

    def _messages_to_text(self, messages):
        text_lines = []
        for message in messages:
            text_lines.append(f'{message.filepath}:{message.line}:{message.column}: {message.message}')
            text_lines.extend(message.details_lines)
            text_lines.extend(self._messages_to_text(message.children))
        return text_lines

    def _extract_categories(self, message, args):
        BUGRISC_CATEGORY='Bug Risk'
        CLARITY_CATEGORY='Clarity'
        COMPATIBILITY_CATEGORY='Compatibility'
        COMPLEXITY_CATEGORY='Complexity'
        DUPLICATION_CATEGORY='Duplication'
        PERFORMANCE_CATEGORY='Performance'
        SECURITY_CATEGORY='Security'
        STYLE_CATEGORY='Style'

        categories = []
        if 'bugprone' in message.diagnostic_name:
            categories.append(BUGRISC_CATEGORY)
        if 'modernize' in message.diagnostic_name:
            categories.append(COMPATIBILITY_CATEGORY)
        if 'portability' in message.diagnostic_name:
            categories.append(COMPATIBILITY_CATEGORY)
        if 'performance' in message.diagnostic_name:
            categories.append(PERFORMANCE_CATEGORY)
        if 'readability' in message.diagnostic_name:
            categories.append(CLARITY_CATEGORY)
        if 'cloexec' in message.diagnostic_name:
            categories.append(SECURITY_CATEGORY)
        if 'security' in message.diagnostic_name:
            categories.append(SECURITY_CATEGORY)
        if 'naming' in message.diagnostic_name:
            categories.append(STYLE_CATEGORY)
        if 'misc' in message.diagnostic_name:
            categories.append(STYLE_CATEGORY)
        if 'cppcoreguidelines' in message.diagnostic_name:
            categories.append(STYLE_CATEGORY)
        if 'hicpp' in message.diagnostic_name:
            categories.append(STYLE_CATEGORY)
        if 'simplify' in message.diagnostic_name:
            categories.append(COMPLEXITY_CATEGORY)
        if 'redundant' in message.diagnostic_name:
            categories.append(DUPLICATION_CATEGORY)
        if message.diagnostic_name.startswith('boost-use-to-string'):
            categories.append(COMPATIBILITY_CATEGORY)
        if len(categories) == 0:
            categories.append(BUGRISC_CATEGORY)
        return remove_duplicates(categories)

    def _extract_trace(self, message, args):
        return {
            'locations': self._extract_other_locations(message, args)
        }

    def _extract_other_locations(self, message, args):
        locations_list = []
        for child in message.children:
            locations_list.append(self._extract_location(child, args))
            locations_list.extend(self._extract_other_locations(child, args))
        return locations_list

    def _extract_location(self, message, args):
        location = {
            'path': message.filepath,
        }
        if args.use_location_lines:
            location['lines'] = {
                'begin': message.line
            }
        else:
            location['positions'] = {
               'begin': {
                   'line': message.line,
                   'column': message.column
               }
            }
        return location

    def _extract_severity(self, message, args):
        if message.level == ClangMessage.Level.NOTE:
            return 'info'
        if message.level == ClangMessage.Level.REMARK:
            return 'minor'
        if message.level == ClangMessage.Level.WARNING:
            return 'major'
        if message.level == ClangMessage.Level.ERROR:
            return 'critical'
        if message.level == ClangMessage.Level.FATAL:
            return 'blocker'

    def _generate_fingerprint(self, message):
        h = hashlib.md5()
        h.update(message.filepath.encode('utf8'))
        h.update(str(message.line).encode('utf8'))
        h.update(str(message.column).encode('utf8'))
        h.update(message.message.encode('utf8'))
        h.update(message.diagnostic_name.encode('utf8'))
        for child in message.children:
            h.update(self._generate_fingerprint(child).encode('utf-8'))
        return h.hexdigest()
