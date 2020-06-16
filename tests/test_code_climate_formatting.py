#!/usr/bin/env python3
import unittest
import unittest.mock
import json

from clang_tidy_converter import CodeClimateFormatter, ClangMessage

class CodeClimateFormatterTest(unittest.TestCase):
    def test_format(self):
        child1 = ClangMessage('/some/file/path1.cpp', 8, 10, ClangMessage.Level.NOTE, 'Allocated here', '', ['return new A;', '       ^'])
        msg = ClangMessage('/some/file/path.cpp', 100, 2, ClangMessage.Level.WARNING, 'Memory leak', 'bugprone-undefined-memory-manipulation.SomethingWrong',
                           ['void a(int)', '          ^'], [child1])
        formatter = CodeClimateFormatter()
        args = unittest.mock.Mock()
        args.use_location_lines = True
        self.assertEqual(
"""{
  "type": "issue",
  "check_name": "bugprone-undefined-memory-manipulation.SomethingWrong",
  "description": "Memory leak",
  "content": {
    "body": "```\\nvoid a(int)\\n          ^\\n/some/file/path1.cpp:8:10: Allocated here\\nreturn new A;\\n       ^\\n```"
  },
  "categories": [
    "Bug Risk"
  ],
  "location": {
    "path": "/some/file/path.cpp",
    "lines": {
      "begin": 100
    }
  },
  "trace": {
    "locations": [
      {
        "path": "/some/file/path1.cpp",
        "lines": {
          "begin": 8
        }
      }
    ]
  },
  "severity": "major",
  "fingerprint": "f2f6ccb970f2259d10e525b4b5805a5c"
}\0
""", formatter.format([msg], args))

    def test_extract_content(self):
        child1 = ClangMessage('/some/file/path1.cpp', 8, 10, ClangMessage.Level.NOTE, 'Allocated here', '', ['return new A;', '       ^'])
        msg = ClangMessage('/some/file/path.cpp', 100, 2, ClangMessage.Level.WARNING, 'Memory leak', 'bugprone-undefined-memory-manipulation.SomethingWrong',
                           ['void a(int)', '          ^'], [child1])
        formatter = CodeClimateFormatter()
        self.assertEqual({
            'body': '\n'.join([
                '```',
                'void a(int)',
                '          ^',
                '/some/file/path1.cpp:8:10: Allocated here',
                'return new A;',
                '       ^',
                '```'])
        }, formatter._extract_content(msg, object()))

    def test_extract_bug_risk_category(self):
        self._test_diagnostic_category('bugprone-use-after-move', 'Bug Risk')

    def test_extract_compatibility_category_1(self):
        self._test_diagnostic_category('modernize-replace-auto-ptr', 'Compatibility')

    def test_extract_compatibility_category_2(self):
        self._test_diagnostic_category('portability-restrict-system-includes', 'Compatibility')

    def test_extract_compatibility_category_3(self):
        self._test_diagnostic_category('boost-use-to-string', 'Compatibility')

    def test_extract_performance_category(self):
        self._test_diagnostic_category('performance-inefficient-algorithm', 'Performance')

    def test_extract_clarity_category_1(self):
        self._test_diagnostic_category('google-readability-avoid-underscore-in-googletest-name', 'Clarity')

    def test_extract_clarity_category_2(self):
        self._test_diagnostic_category('readability-misplaced-array-index', 'Clarity')

    def test_extract_security_category_1(self):
        self._test_diagnostic_category('android-cloexec-open', 'Security')

    def test_extract_security_category_2(self):
        self._test_diagnostic_category('clang-analyzer-security.insecureAPI.bcmp', 'Security')

    def test_extract_style_category_1(self):
        self._test_diagnostic_category('readability-identifier-naming', 'Style')

    def test_extract_style_category_2(self):
        self._test_diagnostic_category('cppcoreguidelines-avoid-goto', 'Style')

    def test_extract_style_category_3(self):
        self._test_diagnostic_category('hicpp-no-assembler', 'Style')

    def test_extract_complexity_category(self):
        self._test_diagnostic_category('readability-simplify-boolean-expr', 'Complexity')

    def test_extract_duplication_category(self):
        self._test_diagnostic_category('misc-redundant-expression', 'Duplication')

    def test_extract_default_category(self):
        self._test_diagnostic_category('cert-dcl16-c', 'Bug Risk')

    def _test_diagnostic_category(self, diagnostic, category):
        msg = ClangMessage(diagnostic_name=diagnostic)
        formatter = CodeClimateFormatter()
        self.assertIn(category, formatter._extract_categories(msg, object()))

    def test_extract_duplicated_categories(self):
        msg = ClangMessage(diagnostic_name='cppcoreguidelines-readability-avoid-goto')
        formatter = CodeClimateFormatter()
        categories = formatter._extract_categories(msg, object())
        self.assertEqual(2, len(categories))
        self.assertIn('Style', categories)
        self.assertIn('Clarity', categories)

    def test_extract_trace_lines(self):
        child1 = ClangMessage('/some/file/path1.cpp', 8, 10)
        msg = ClangMessage('/some/file/path.cpp', 100, 2, children=[child1])
        formatter = CodeClimateFormatter()
        args = unittest.mock.Mock()
        args.use_location_lines = True
        self.assertEqual({
            'locations': [
                {
                    'path': '/some/file/path1.cpp',
                    'lines': {
                        'begin': 8
                    }
                }
            ]
        }, formatter._extract_trace(msg, args))

    def test_extract_trace_positions(self):
        child1 = ClangMessage('/some/file/path1.cpp', 8, 10)
        msg = ClangMessage('/some/file/path.cpp', 100, 2, children=[child1])
        formatter = CodeClimateFormatter()
        args = unittest.mock.Mock()
        args.use_location_lines = False
        self.assertEqual({
            'locations': [
                {
                    'path': '/some/file/path1.cpp',
                    'positions': {
                        'begin': {
                            'line': 8,
                            'column': 10
                        }
                    }
                }
            ]
        }, formatter._extract_trace(msg, args))

    def test_extract_location_lines(self):
        msg = ClangMessage('/some/file/path.cpp', 100, 2)
        formatter = CodeClimateFormatter()
        args = unittest.mock.Mock()
        args.use_location_lines = True
        self.assertEqual({
            'path': '/some/file/path.cpp',
            'lines': {
                'begin': 100
            }
        }, formatter._extract_location(msg, args))

    def test_extract_location_positions(self):
        msg = ClangMessage('/some/file/path.cpp', 100, 2)
        formatter = CodeClimateFormatter()
        args = unittest.mock.Mock()
        args.use_location_lines = False
        self.assertEqual({
            'path': '/some/file/path.cpp',
            'positions': {
                'begin': {
                    'line': 100,
                    'column': 2
                }
            }
        }, formatter._extract_location(msg, args))

    def test_extracting_note_severity(self):
        self._test_extracting_severity(ClangMessage.Level.NOTE, 'info')

    def test_extracting_remark_severity(self):
        self._test_extracting_severity(ClangMessage.Level.REMARK, 'minor')

    def test_extracting_warning_severity(self):
        self._test_extracting_severity(ClangMessage.Level.WARNING, 'major')

    def test_extracting_error_severity(self):
        self._test_extracting_severity(ClangMessage.Level.ERROR, 'critical')

    def test_extracting_fatal_severity(self):
        self._test_extracting_severity(ClangMessage.Level.FATAL, 'blocker')

    def _test_extracting_severity(self, level, severity_str):
        msg = ClangMessage(level=level)
        formatter = CodeClimateFormatter()
        self.assertEqual(severity_str, formatter._extract_severity(msg, object()))

    def test_generate_fingerprint_reproducibility(self):
        msg1 = ClangMessage('path1', line=1)
        msg2 = ClangMessage('path1', line=1)
        formatter = CodeClimateFormatter()
        self.assertEqual(formatter._generate_fingerprint(msg1), formatter._generate_fingerprint(msg2))

    def test_generate_fingerprint_uses_filepath(self):
        self._test_fingerprints_different(ClangMessage('/path/to/file1.cpp'), ClangMessage('/path/to/file2.cpp'))

    def test_generate_fingerprint_uses_line(self):
        self._test_fingerprints_different(ClangMessage(line=1), ClangMessage(line=2))

    def test_generate_fingerprint_uses_column(self):
        self._test_fingerprints_different(ClangMessage(column=1), ClangMessage(column=2))

    def test_generate_fingerprint_uses_message(self):
        self._test_fingerprints_different(ClangMessage(message='A'), ClangMessage(message='B'))

    def test_generate_fingerprint_uses_diagnostic_name(self):
        self._test_fingerprints_different(ClangMessage(diagnostic_name='A'), ClangMessage(diagnostic_name='B'))

    def test_generate_fingerprint_uses_children(self):
        child1 = ClangMessage(line=1)
        child2 = ClangMessage(line=2)
        self._test_fingerprints_different(ClangMessage(children=[child1]), ClangMessage(children=[child2]))

    def _test_fingerprints_different(self, msg1, msg2):
        formatter = CodeClimateFormatter()
        self.assertNotEqual(formatter._generate_fingerprint(msg1), formatter._generate_fingerprint(msg2))
