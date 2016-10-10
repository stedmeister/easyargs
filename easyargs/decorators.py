import parsers

def make_easy_args(obj):
    def internal_func(*args, **kwargs):
        parser = parsers.create_base_parser(obj)
        parsers.function_parser(obj, parser)
        parsers.handle_parser(parser)

    return internal_func
