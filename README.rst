easyargs
========

A project designed to make command line argument parsing easy.

It is used as follows:

    import easyargs

    @easyargs
    def main(name, count=1, greeting='Hello'):
        """A simple greeting program"""
        for i in range(count):
            print '{greeting} {name}!'.format(greeting=greeting, name=name)


    if __name__ == '__main__':
        main()

In this (rather contrived) example, main will be inspected and the arg keywords
will be turned into positional arguments and the kwarg keywords will be turned
into optional arguments.  This can be seen if we run the above script with the
help flag:

    $ python simple.py -h
    usage: simple_test.py [-h] [--count COUNT] [--greeting GREETING] name

    A simple greeting program

    positional arguments:
      name

    optional arguments:
      -h, --help           show this help message and exit
      --count COUNT
      --greeting GREETING

Note are that program description is automatically created
based on the docstring of the function.  Also note that the type of the default
value is inspected so that the value of count is coerced to an integer.

    $ python simple.py World
    Hello World

    $ python simple.py everybody --count 2 --greeting Hola
    Hola everybody!
    Hola everybody!
