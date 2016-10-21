from . import parsers
import functools
import inspect

def make_easy_args(obj=None, auto_call=True):
    def decorate(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            parser = parsers.create_base_parser(f)
            if inspect.isfunction(f):
                parsers.function_parser(f, parser)
            else:
                klass_instance = f()
                parsers.class_parser(klass_instance, parser)
            if auto_call:
                parsers.handle_parser(parser)


            return parser
        return decorated

    if obj != None:
        return decorate(obj)

    return decorate
