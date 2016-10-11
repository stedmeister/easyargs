import unittest
import mock

import easyargs

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
        self.assertEqual(result, { 'name': 'person', 'count': None, 'greeting': None })

        result = parser.parse_args(['person', '--count', '4'])
        result = vars(result)
        del result['func']
        self.assertEqual(result, { 'name': 'person', 'count': 4, 'greeting': None })
