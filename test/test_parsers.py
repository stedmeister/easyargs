from __future__ import print_function

import unittest
import mock
import six

import easyargs


class SysExitCalled(Exception):
    """This exception will be thrown when sys.exit is called.  This
       is needed to 'halt' program execution."""


def parser_test_helper(parser,
                       call_function,
                       arguments,
                       expected_values,
                       exit_expected):

    mocked_sysv = [__name__] + arguments

    @mock.patch('sys.argv', mocked_sysv)
    @mock.patch('sys.stdout', new_callable=six.StringIO)
    @mock.patch('sys.stderr', new_callable=six.StringIO)
    @mock.patch('sys.exit')
    def handle_parser_call(exit_called, stderr, stdout):
        exit_called.side_effect = SysExitCalled('sys.exit()')
        try:
            parser()
        except SysExitCalled:
            pass

        assert(exit_called.called == exit_expected)
        if not exit_called.called:
            if expected_values is None:
                call_function.assert_not_called()
            else:
                call_function.assert_called_with(*expected_values)
        return stdout, stderr

    stdout, stderr = handle_parser_call()
    return stdout.getvalue(), stderr.getvalue()


# Work out how to mock the function
class TestDecorator(unittest.TestCase):

    def test_with_no_options(self):
        @easyargs
        def main_test_case_no_options(foo, bar=1):
            pass

        with mock.patch('sys.argv', [__name__, 'foo_value']):
            main_test_case_no_options()

    def test_with_options(self):
        @easyargs()
        def main_test_case_with_options(foo, bar=1):
            pass

        with mock.patch('sys.argv', [__name__, 'bar_value']):
            main_test_case_with_options()

    def test_can_handle_function_with_no_arguments(self):
        @easyargs
        def main_with_no_args():
            pass

        with mock.patch('sys.argv', [__name__]):
            main_with_no_args()

    def test_can_handle_functions_with_only_positional_args(self):
        @easyargs
        def main_with_only_pos_args(arg1, arg2, arg3):
            pass

        with mock.patch('sys.argv', [__name__, 'a1', 'a2', 'a3']):
            main_with_only_pos_args()

    def test_can_handle_functions_with_only_optional_args(self):
        @easyargs
        def main_with_only_opt_args(arg1=None, arg2=None, arg3=None):
            pass

        with mock.patch('sys.argv', [__name__, '--arg1', '1', '--arg3', '3', '--arg2', '2']):
            main_with_only_opt_args()


class TestSampleInterfaces(unittest.TestCase):
    def test_function_is_actually_called(self):

        called = mock.MagicMock()

        @easyargs
        def main(name, count=1, greeting='Hello'):
            called(name, count, greeting)

        with mock.patch('sys.argv', [__name__, 'Joe']):
            main()
            called.assert_called_with('Joe', 1, 'Hello')

    def test_example(self):

        @easyargs(auto_call=False)
        def main(name, count=1, greeting='Hello'):
            """A simple greeting program"""
            pass

        parser = main()
        self.assertEqual(parser.description, 'A simple greeting program')
        result = parser.parse_args(['person'])
        result = vars(result)
        del result['func']
        self.assertEqual(result, {'name': 'person', 'count': 1, 'greeting': 'Hello'})

        result = parser.parse_args(['person', '--count', '4'])
        result = vars(result)
        del result['func']
        self.assertEqual(result, {'name': 'person', 'count': 4, 'greeting': 'Hello'})


class TestGitCloneExample(unittest.TestCase):
    def setUp(self):
        called = mock.MagicMock()
        self.function_called = called

        @easyargs
        class GitClone(object):
            """A git clone"""

            def clone(self, src, _dest):
                """Clone a repository"""
                called(src, _dest)

            def commit(self, a=False, m=None, amend=False):
                """Commit a change to the index"""
                called(a, m, amend)

        self.parser = GitClone

    def test_help_text(self):
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['-h'],
                                            None,
                                            True)
        self.assertTrue('usage: test_parsers [-h]' in stdout)
        self.assertTrue('A git clone' in stdout)
        self.assertTrue('clone         Clone a repository' in stdout)
        self.assertTrue('commit        Commit a change to the index' in stdout)

    def test_simple_clone(self):
        """A test to ensure that basic argument parsing works"""
        parser_test_helper(self.parser,
                           self.function_called,
                           ['clone', 'git@github.com/user/repo'],
                           ('git@github.com/user/repo', None),
                           False)

    def test_invalid_clone_parameters(self):
        """Make sure that an error is raised when not enough arguments are parsed"""
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['clone'],
                                            None,
                                            True)

        # Output signature changed in python 3, so must assert on part of message
        self.assertTrue("""usage: test_parsers clone [-h] src [dest]
test_parsers clone: error:""" in stderr)

    def test_commit_no_parameters(self):
        """This tests just the commit parameters i.e. git commit"""
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['commit'],
                                            (False, None, False),
                                            False)

    def test_commit_add_no_message(self):
        """This tests the equivalent of git commit -a"""
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['commit', '-a'],
                                            (True, None, False),
                                            False)

    def test_commit_with_message(self):
        """This tests the equivalent of git commit -m "message" """
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['commit', '-m', 'This is my message'],
                                            (False, 'This is my message', False),
                                            False)

    def test_commit_with_amend_flag(self):
        """This is the equivalent to git commit --amend"""
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['commit', '--amend'],
                                            (False, None, True),
                                            False)

    def test_commit_with_all_options(self):
        """This is the equivalent to git commit -am "Foo" --amend"""
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['commit', '-am', 'Foo', '--amend'],
                                            (True, 'Foo', True),
                                            False)


class TestParsersWithArgHelpers(unittest.TestCase):
    def setUp(self):
        called = mock.MagicMock()
        self.function_called = called

        @easyargs
        class GitClone(object):
            """A git clone"""

            def clone(self, src, _dest):
                """
                Clone a repository
                :param src: the repository to clone
                :param _dest: the destination for cloning
                """
                called(src, _dest)

            def commit(self, a=False, m=None, amend=False):
                """
                Commit a change to the index
                :param a: Add all modified flags to the index
                :param amend: Amend the last commit
                """
                called(a, m, amend)

        self.parser = GitClone

    def test_param_info_removed_from_help(self):
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['-h'],
                                            None,
                                            True)
        print(stdout)
        usage_string = ('usage: test_parsers [-h] {clone,commit}' in stdout) or \
                       ('usage: test_parsers [-h] {commit,clone}' in stdout)
        self.assertTrue(usage_string)
        self.assertTrue('clone         Clone a repository' in stdout)
        self.assertTrue('commit        Commit a change to the index' in stdout)
        self.assertTrue('param' not in stdout)

    def test_clone_help_text(self):
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['clone', '-h'],
                                            None,
                                            True)

        self.assertTrue('usage: test_parsers clone [-h] src [dest]' in stdout)
        self.assertTrue('src         the repository to clone' in stdout)
        self.assertTrue('dest        the destination for cloning' in stdout)
        self.assertTrue('param' not in stdout)

    def test_commit_help_text_missing_parser(self):
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['commit', '-h'],
                                            None,
                                            True)

        self.assertTrue('usage: test_parsers commit [-h] [-a] [-m M] [--amend]' in stdout)
        self.assertTrue('-a          Add all modified flags to the index' in stdout)
        self.assertTrue('-m M\n' in stdout)
        self.assertTrue('--amend     Amend the last commit' in stdout)
        self.assertTrue('param' not in stdout)


class TestParsersWithPoorFormattedArgParsers(unittest.TestCase):
    def setUp(self):
        called = mock.MagicMock()
        self.function_called = called

        @easyargs
        def poor_formatting(src, _dest):
            """
            Clone a repository
            :    param src: the repository to clone
            :param    _dest     : the destination for cloning
            """
            called(src, _dest)

        self.parser = poor_formatting

    def test_doc_text_formatting(self):
        stdout, stderr = parser_test_helper(self.parser,
                                            self.function_called,
                                            ['-h'],
                                            None,
                                            True)

        self.assertTrue('usage: test_parsers [-h] src [dest]' in stdout)
        self.assertTrue('src         the repository to clone' in stdout)
        self.assertTrue('dest        the destination for cloning' in stdout)
        self.assertTrue('param' not in stdout)


class TestFunctionValueReturned(unittest.TestCase):
    def setUp(self):
        @easyargs
        def return_some_value(value=5):
            return value

        self.parser = return_some_value

    @mock.patch('sys.argv', [__name__])
    def test_a_value_is_returned(self):
        result = self.parser()
        self.assertEqual(result, 5)


class TestValueReturnedWhenNotUsingAutoCall(unittest.TestCase):
    """Tests that the auto_call=False is not clobbered, although
    this is mainly used for testing."""
    def setUp(self):
        @easyargs(auto_call=False)
        def return_some_value(value=5):
            return value

        self.parser = return_some_value

    @mock.patch('sys.argv', [__name__])
    def test_a_value_is_returned(self):
        parser = self.parser()
        from easyargs import parsers
        result = parsers.handle_parser(parser)
        self.assertEqual(result, 5)
