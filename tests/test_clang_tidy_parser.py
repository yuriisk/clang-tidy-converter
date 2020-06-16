#!/usr/bin/env python3

import unittest

from clang_tidy_converter import ClangTidyParser, ClangMessage

class ClangTidyParserTest(unittest.TestCase):
    def test_warning_message(self):
        parser = ClangTidyParser()
        messages = parser.parse(['/usr/lib/include/some_include.h:1039:3: warning: Potential memory leak [clang-analyzer-cplusplus.NewDeleteLeaks]'])
        self.assertEqual(1, len(messages))
        msg = messages[0]
        self.assertEqual('/usr/lib/include/some_include.h', msg.filepath)
        self.assertEqual(1039, msg.line)
        self.assertEqual(3, msg.column)
        self.assertEqual(ClangMessage.Level.WARNING, msg.level)
        self.assertEqual('Potential memory leak', msg.message)
        self.assertEqual('clang-analyzer-cplusplus.NewDeleteLeaks', msg.diagnostic_name)
        self.assertEqual([], msg.details_lines)
        self.assertEqual([], msg.children)

    def test_remark_message_level(self):
        parser = ClangTidyParser()
        messages = parser.parse(['/usr/lib/include/some_include.h:1039:3: remark: Potential memory leak [clang-analyzer-cplusplus.NewDeleteLeaks]'])
        msg = messages[0]
        self.assertEqual(ClangMessage.Level.REMARK, msg.level)

    def test_error_message_level(self):
        parser = ClangTidyParser()
        messages = parser.parse(['/usr/lib/include/some_include.h:1039:3: error: Potential memory leak [clang-analyzer-cplusplus.NewDeleteLeaks]'])
        msg = messages[0]
        self.assertEqual(ClangMessage.Level.ERROR, msg.level)

    def test_fatal_message_level(self):
        parser = ClangTidyParser()
        messages = parser.parse(['/usr/lib/include/some_include.h:1039:3: fatal: Potential memory leak [clang-analyzer-cplusplus.NewDeleteLeaks]'])
        msg = messages[0]
        self.assertEqual(ClangMessage.Level.FATAL, msg.level)

    def test_unknown_message_level(self):
        parser = ClangTidyParser()
        messages = parser.parse(['/usr/lib/include/some_include.h:1039:3: fatal: Potential memory leak [clang-analyzer-cplusplus.NewDeleteLeaks]',
                                 '/usr/lib/include/some_include.h:1039:3: smth: Potential memory leak [clang-analyzer-cplusplus.NewDeleteLeaks]'])
        self.assertEqual(1, len(messages))
        msg = messages[0]
        self.assertEqual(['/usr/lib/include/some_include.h:1039:3: smth: Potential memory leak [clang-analyzer-cplusplus.NewDeleteLeaks]'], msg.details_lines)

    def test_multiline_warning_message(self):
        parser = ClangTidyParser()
        messages = parser.parse(['/usr/lib/include/some_include.h:1039:3: warning: Potential memory leak [clang-analyzer-cplusplus.NewDeleteLeaks]',
                                 '  return new SomeFunction(',
                                 '  ^'])
        self.assertEqual(1, len(messages))
        msg = messages[0]
        self.assertEqual('/usr/lib/include/some_include.h', msg.filepath)
        self.assertEqual(1039, msg.line)
        self.assertEqual(3, msg.column)
        self.assertEqual(ClangMessage.Level.WARNING, msg.level)
        self.assertEqual('Potential memory leak', msg.message)
        self.assertEqual('clang-analyzer-cplusplus.NewDeleteLeaks', msg.diagnostic_name)
        self.assertEqual(['  return new SomeFunction(',
                          '  ^'], msg.details_lines)
        self.assertEqual([], msg.children)

    def test_warning_message_children(self):
        parser = ClangTidyParser()
        messages = parser.parse(['/usr/lib/include/some_include.h:1039:3: warning: Potential memory leak [clang-analyzer-cplusplus.NewDeleteLeaks]',
                                 '  return new SomeFunction(',
                                 '  ^',
                                 '/home/user/some_source.cpp:267:15: note: Calling \'OtherFunction\'',
                                 '    auto sf = OtherFunction( a, b, c );',
                                 '              ^'])
        self.assertEqual(1, len(messages))
        msg = messages[0]
        self.assertEqual('/usr/lib/include/some_include.h', msg.filepath)
        self.assertEqual(1039, msg.line)
        self.assertEqual(3, msg.column)
        self.assertEqual(ClangMessage.Level.WARNING, msg.level)
        self.assertEqual('Potential memory leak', msg.message)
        self.assertEqual('clang-analyzer-cplusplus.NewDeleteLeaks', msg.diagnostic_name)
        self.assertEqual(['  return new SomeFunction(',
                          '  ^'], msg.details_lines)
        self.assertEqual(1, len(msg.children))
        child = msg.children[0]
        self.assertEqual('/home/user/some_source.cpp', child.filepath)
        self.assertEqual(267, child.line)
        self.assertEqual(15, child.column)
        self.assertEqual(ClangMessage.Level.NOTE, child.level)
        self.assertEqual('Calling \'OtherFunction\'', child.message)
        self.assertEqual('', child.diagnostic_name)
        self.assertEqual(['    auto sf = OtherFunction( a, b, c );',
                          '              ^'], child.details_lines)
        self.assertEqual([], child.children)

    def test_ignorance_of_generic_errors(self):
        parser = ClangTidyParser()
        messages = parser.parse(['error: -mapcs-frame not supported'])
        self.assertEqual([], messages)

if __name__ == '__main__':
    unittest.main()
