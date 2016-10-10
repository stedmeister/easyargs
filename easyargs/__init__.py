import decorators
import sys

# This bit of magic allows us to use the module name as a decorator
sys.modules[__name__] = decorators.make_easy_args
