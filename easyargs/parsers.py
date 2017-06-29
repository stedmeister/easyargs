import inspect
import argparse
import six
import re


def handle_parser(parser):
    args = vars(parser.parse_args())

    # Get the handler function
    try:
        function = args.pop('func')
    except KeyError:
        return

    # Call the original function with the parser args
    return function(**args)


def parser_help_text(help_text):
    """Takes the help text supplied as a doc string and extraxts the
    description and any param arguments."""
    if help_text is None:
        return None, {}

    main_text = ''
    params_help = {}

    for line in help_text.splitlines():
        line = line.strip()
        match = re.search(r':\s*param\s*(?P<param>\w+)\s*:(?P<help>.*)$', line)
        if match:
            params_help[match.group('param')] = match.group('help').strip()
        else:
            main_text += line

    return main_text, params_help


def create_base_parser(obj):
    # Get the help text for the function
    help_text = inspect.getdoc(obj)
    main_text, params_help = parser_help_text(help_text)

    parser = argparse.ArgumentParser(description=main_text)
    return parser


def calculate_default_type(arg, has_default, default_value, params_help):
    """This function looks at the default value and returns the type that
       should be supplied to the parser"""
    positional = True
    arg_params = {}
    arg_name = arg

    # Check to see if we have help text for this argument
    try:
        arg_params['help'] = params_help[arg_name]
    except KeyError:
        pass

    # If we have a default value, then this is not positional
    if has_default:
        positional = False

    # Special case when a base type is supplied
    if default_value in (int, float):
        positional = True

    # For boolean options, change the action
    if default_value is True:
        arg_params['action'] = 'store_false'
    elif default_value is False:
        arg_params['action'] = 'store_true'

    # Finally, check if the default value is an integer or a float
    # and set the arg type on the item
    if type(default_value) in (int, float):
        arg_params['type'] = type(default_value)

    # Update the arg_name
    if positional:
        if arg_name.startswith('_'):
            arg_params['nargs'] = '?'
            arg_params['default'] = None
            arg_params['metavar'] = arg_name.lstrip('_')
            #arg_name = arg_name.lstrip('_')
    else:
        arg_params['default'] = default_value
        if len(arg_name) == 1:
            arg_name = '-' + arg_name
        else:
            arg_name = '--' + arg_name

    return arg_name, arg_params


def function_parser(function, parser):
    """This function parses a function and adds its arguments to the supplied parser"""

    # Store the function pointer on the parser for later use
    parser.set_defaults(func=function)

    # Get the help text and parse it for params
    help_text = inspect.getdoc(function)
    main_text, params_help = parser_help_text(help_text)

    # Get the function information
    args, varargs, keywords, defaults = inspect.getargspec(function)
    if args is None:
        args = []

    if defaults is None:
        defaults = []

    # If the function is a class method, it will have a self that needs to be removed
    if len(args) and args[0] == 'self':
        args.pop(0)

    # Work out whether the argument has a default by subtracting the length
    # of the default args from the number of arguments
    num_required_args = len(args) - len(defaults)
    for idx, arg in enumerate(args):
        if idx < num_required_args:
            arg_name, arg_params = calculate_default_type(arg, False, None, params_help)
        else:
            default_value = defaults[idx - num_required_args]
            arg_name, arg_params = calculate_default_type(arg, True, default_value, params_help)

        parser.add_argument(arg_name, **arg_params)


def filter_private_methods(method):
    """Simple filter method.  Ignores private functions"""
    return not method.startswith('_')


def class_parser(klass, parser, method_filter=filter_private_methods):
    # Create a subparser object to handle the sub commands
    subparsers = parser.add_subparsers(help='sub-command help')

    # Find all of the methods in the object instance
    all_methods = inspect.getmembers(klass, inspect.ismethod)

    # Let's filter the list down to what we actually want to expose
    methods_to_expose = [m for m in all_methods if method_filter(m[0])]

    # Let's now create a sub parser for each method found
    for name, method in methods_to_expose:
        help_text = inspect.getdoc(method)
        main_text, params_help = parser_help_text(help_text)
        method_parser = subparsers.add_parser(name, help=main_text)
        function_parser(method, method_parser)
