from __future__ import print_function

import unittest
import mock
import six

from easyargs.parsers import parser_help_text


class TestHelpText(unittest.TestCase):
    def test_no_params_help(self):
        input = """A simple greeting program
    """
        main_text, params_help = parser_help_text(input)
        self.assertEqual(main_text, 'A simple greeting program')
        self.assertEqual(params_help, {})

    def test_simple_use_case(self):
        input = """A simple greeting program
    :param name:      Name to greet.
    :param count:     How many times to greet them.
    :param greeting:  Which greeting to use.
    """
        main_text, params_help = parser_help_text(input)
        self.assertEqual(main_text, 'A simple greeting program')
        self.assertEqual(params_help, {
            'name': 'Name to greet.',
            'count': 'How many times to greet them.',
            'greeting': 'Which greeting to use.'
        })

    def test_no_main_text(self):
        input = """
    :param name:      Name to greet.
    :param count:     How many times to greet them.
    :param greeting:  Which greeting to use.
    """
        main_text, params_help = parser_help_text(input)
        self.assertEqual(main_text, '')
        self.assertEqual(params_help, {
            'name': 'Name to greet.',
            'count': 'How many times to greet them.',
            'greeting': 'Which greeting to use.'
        })

    def test_random_white_space(self):
        input = """A simple greeting program
        :param name:      Name to greet.
    :  param count:              How many times to greet them.
    : param       greeting  :  Which greeting to use.
    """
        main_text, params_help = parser_help_text(input)
        self.assertEqual(main_text, 'A simple greeting program')
        self.assertEqual(params_help, {
            'name': 'Name to greet.',
            'count': 'How many times to greet them.',
            'greeting': 'Which greeting to use.'
        })
