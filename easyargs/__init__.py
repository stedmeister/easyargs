from . import decorators, parsers
import sys

# This bit of magic allows us to use the module name as a decorator
decorators.make_easy_args.parsers = parsers
decorators.make_easy_args.decorators = decorators

sys.modules[__name__] = decorators.make_easy_args
