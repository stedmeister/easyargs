#! /usr/bin/env python
"""easycmdline is a wrapper around argparse.  argparse is a great cmdline
   utility, but the options can be complicated.  This module aims to be a
   simple wrapper around the module"""

from __future__ import print_function
import argparse
import inspect


def filter_private_methods(method):
    return not method.startswith('_')


def get_default_type(value):
    TYPES = (int, str)
    if type(value) == type:
        found_type = value
    else:
        found_type = type(value)

    if found_type in TYPES:
        return found_type
    return None


def create_sub_parser(parser, method_info):
    name, method = method_info

    # Try to get the docstring for the help text
    help_text = inspect.getdoc(method)
    if help_text is None:
        help_text = '{n} help'.format(n=name)

    local_parser = parser.add_parser(name, help=help_text)

    # Get the arguments for the method
    # TODO: do something sensible with args and varargs
    try:
        args, _, _, defaults, _, _, _ = inspect.getfullargspec(method)
    except AttributeError:
        args, _, _, defaults = inspect.getargspec(method)

    num_positional = len(args)
    if defaults is not None:
        num_positional -= len(defaults)

    for idx, arg in enumerate(args):
        # Work out whether arg is positional or optional
        if idx < num_positional:
            if arg != 'self':
                local_parser.add_argument(arg)
        else:
            # Get the default value so that we can coerce it
            default_value = defaults[idx - num_positional]
            print(arg, default_value)
            default_type = get_default_type(default_value)
            action = 'store'
            if default_value:
                action = 'store_false'
            else:
                action = 'store_true'

            if default_type is not None:
                print(arg, default_type, action)
                local_parser.add_argument('--' + arg, type=default_type, action=action)
            else:
                local_parser.add_argument('--' + arg, action=action)

        # Store the method on the parser so we can call it later
        local_parser.set_defaults(func=method)


def get_parser(object_instance, method_filter=filter_private_methods):
    # Create a top level parser and a sub parser object
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')

    # Find all of the methods in the object instance
    all_methods = inspect.getmembers(object_instance, inspect.ismethod)

    # Let's filter the list down to what we actually want to expose
    methods_to_expose = [m for m in all_methods if method_filter(m[0])]

    # Let's now create a sub parser for each method found
    for method_info in methods_to_expose:
        create_sub_parser(subparsers, method_info)

    return parser


def handle_args(args):
    # Convert args to a dict
    args = vars(args)

    # Get the function to call
    func = args.pop('func')

    # Strip out not supplied arguments
    actual_args = {}
    for arg, value in args.iteritems():
        if value is not None:
            actual_args[arg] = value

    print(func, actual_args)
    func(**actual_args)


def handle_parser(object_instance, method_filter=filter_private_methods):
    parser = get_parser(object_instance, method_filter)
    args = parser.parse_args()
    print(args)
    handle_args(args)


class Base(object):
    def base(self, think):
        print('base')

    def _private(self):
        print('_private')


def j():
    print('JJJJJ')


class Top(Base):
    def top(self, a, b='default'):
        """This is the top function that does things

        It is also helpful

        a: blah
        b: default
        """
        print(a, b)

    def test(self, thing=3, foo=False):
        print('test', thing)

    def _bottom(self, c, d):
        print(c, d)


def main():
    t = Top()
    handle_parser(t)


if __name__ == '__main__':
    main()
