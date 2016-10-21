.. image:: https://travis-ci.org/stedmeister/easyargs.svg?branch=master
    :target: https://travis-ci.org/stedmeister/easyargs

easyargs
========

A project designed to make command line argument parsing easy.

There are many ways to create a command line parser in python: argparse, docopt,
click.  These are all great options, but require quite a lot of configuration
and sometimes you just need a function to be called.  Enter easyargs.  Define
the function that you want to be called, decorate it and let easyargs work out
the command line.  This is probably best shown with an example that takes one
required argument and two optional ones:

.. code:: python

    import easyargs

    @easyargs
    def main(name, count=1, greeting='Hello'):
        """A simple greeting program"""
        for i in range(count):
            print '{greeting} {name}!'.format(greeting=greeting, name=name)


    if __name__ == '__main__':
        main()

In this example, main is inspected, the arg keywords are turned into
positional arguments and the kwarg keywords will be turned
into optional arguments.  This can be seen if we run the above script with the
help flag:

.. code::

    $ python simple.py -h
    usage: simple_test.py [-h] [--count COUNT] [--greeting GREETING] name

    A simple greeting program

    positional arguments:
      name

    optional arguments:
      -h, --help           show this help message and exit
      --count COUNT
      --greeting GREETING

A few things worth noting.  Firstly, the description is taken from the docstring
of the function.  Secondly, there is no need to convert count to an integer.
Because the default argument is of type int, the value is coerced to an integer:

.. code::

    $ python simple.py World
    Hello World

    $ python simple.py everybody --count 2 --greeting Hola
    Hola everybody!
    Hola everybody!

How to define the function
--------------------------

The goal of easyargs is to avoid having complicated configuration parameters,
and let the function specify things, however, the following list of rules might
be useful:

- main(arg): arg is a required positional argument
- main(_arg): arg is an optional positional argument
- main(arg=int, _arg=int): Setting a default value as a basic type will keep
                           the argument positional, but coerce it to that type
                           only tested with int / float
- main(arg=list): Setting a default argument as a list will consume multiple
                  arguments from the command line.  It doesn't make sense to
                  supply this more than once.
- main(arg=value): Creates an optional argument with a default value of value
- main(arg=3): If the default value is of type int / float.  Then if a value is
               set it will be coerced to the type.
- main(arg=True): If the default value is of type bool, then arg becomes a flag
                  option.
- main(a=values): If the argument has a length of 1, then it will create a short
                  argument.


Sub commands
------------

Whilst having a simple function parser is great, sometimes you need to have a
sub parser.  This can be created by wrapping a number of functions in a class.
Let's demonstrate this with another example by duplicating part of the git
command:

.. code:: python

    import easyargs

    @easyargs
    class GitClone(object):
        """A git clone"""

        def clone(self, src, _dest):
            """Clone a repository"""

        def commit(self, a=False, m=None, amend=False):
            """Commit a change to the index"""

    if __name__ == '__main__':
        GitClone()

Let's see what this looks like on the command line:

.. code::

    $ python examples/git_clone.py -h
    usage: git_clone.py [-h] {clone,commit} ...

    A git clone

    positional arguments:
      {clone,commit}  sub-command help
        clone         Clone a repository
        commit        Commit a change to the index

    optional arguments:
      -h, --help      show this help message and exit

    $ python examples/git_clone.py clone
    usage: git_clone.py clone [-h] src [dest]
    git_clone.py clone: error: too few arguments

    $ python examples/git_clone.py clone -h
    usage: git_clone.py clone [-h] src [dest]

    positional arguments:
      src
      dest

    optional arguments:
      -h, --help  show this help message and exit

    $ python examples/git_clone.py commit -am "Message"
