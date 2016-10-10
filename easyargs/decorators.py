import parsers
import functools

def make_easy_args(obj=None, auto_call=True):
    def decorate(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            parser = parsers.create_base_parser(f)
            parsers.function_parser(f, parser)
            if auto_call:
                parsers.handle_parser(parser)


            return parser
        return decorated

    if obj != None:
        return decorate(obj)

    return decorate
