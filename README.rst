micro python piper (forget awk)
===============================

From the genial idea by Toby Rosen, pyp:
http://code.google.com/p/pyp/


How to install::

 pip install git+https://github.com/danse/micropyp.git

How to play? Given a ``test`` file containing::

 2
 3
 4

Process it line by line with piped python evaluable statements (no
assignments). ``p`` has always the result returned by the previous pipe stage,
``pp`` is the whole list::

 micropyp.py ' int(p) | sum(pp) ' < test
 7

A quite contorted example, find the file with the oldest change time in a
directory::

 find | micropyp.py 'p, os.stat(p).st_ctime | p[0], datetime.datetime.fromtimestamp(p[1]) | min(pp, key=lambda x:x[1]) | [str(i) for i in p]'

You can wrap it up in a good old bash function, and play with it around::

 oldest_in () { find $1 | micropyp.py 'p, os.stat(p).st_ctime | p[0], datetime.datetime.fromtimestamp(p[1]) | min(pp, key=lambda x:x[1]) | [str(i) for i in p]'; }
 oldest_in <that_dir>

If you get exceptions, they are going to standard output. They are not going to
your next unix pipe stage and you can filter them out using ``2> /dev/null``.

Other examples
--------------

Following examples can be ran like the one before. They are written this way to
work also like actual automatic tests.

    >>> from micropyp import test
    >>> input = '''
    ... 234 4 6
    ... 2323 5 2
    ... 6546 7 5
    ... 675
    ... '''
    >>> test('p.split() | p[2] | int(p) - 3', input)
    3
    -1
    2

Other kinds of processing steps
-------------------------------

    Aside from ``|``, other kinds of pipe serialization are made up with the
    bitwise comparison operators ``^`` and ``&``.

Produce
.......

    The result of ``^`` is iterated, so it acts like a multiplier. Use it
    instead of ``|`` to make the downstream pipe stage iterate the result of a
    preceding pipe stage:

    >>> test('p.split() ^ "flattened "+p', input)
    flattened 234
    flattened 4
    flattened 6
    flattened 2323
    flattened 5
    flattened 2
    flattened 6546
    flattened 7
    flattened 5
    flattened 675
    >>> test('p | p', 'iterable')
    iterable
    >>> test('p ^ p', 'iterable')
    i
    t
    e
    r
    a
    b
    l
    e

Reduce
......

    The result of ``&`` is converted to boolean, and it feeds the downstream
    stage just if turns to be True. It doesn't feeds the downstream stage with
    its result (after all, it's just True or False), but with it's original
    ``p`` value.

    >>> test('p.split() ^  2 < int(p) < 10 &', input)
    4
    6
    5
    7
    5
    >>> input = '''
    ... just noise
    ... use it like grep
    ... if you want
    ... '''
    >>> test(' "grep" in p &', input)
    use it like grep
