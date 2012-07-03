.. image:: https://secure.travis-ci.org/danse/pyper.png
   :align: right

Python piper
============

From the genial idea by Toby Rosen, pyp: http://code.google.com/p/pyp/


How to install? Copy pyper.py on a server and make it executable, or install it
in a virtualenv, or in your system if you have root permissions::

 pip install git+https://github.com/danse/pyper.git

Pyper should work with python 2.6+ (python 3 included). How to play? Given a
``test`` file containing::

 2
 3
 4

Process it line by line with piped python evaluable statements (no
assignments). ``p`` has always the result returned by the previous pipe stage,
``pp`` is the whole list::

 pyper.py ' int(p) | sum(pp) ' < test
 9

Feed it with unix pipes, and forget ``awk``! For example, the following will
ist the ten top-level directories containing more files, excluding hidden files
and dirs (this requires python 2.7 for the Counter)::

 find | pyper.py ' "/." not in p & p.split("/") | p[1] | collections.Counter(pp).most_common(10) '

The same, but at any level::

 find | pyper.py ' "/." not in p & p.split("/") | p[:-2] | "/".join(p) | collections.Counter(pp).most_common(10) '

A quite contorted example, find the file with the oldest change time in a
directory::

 find | pyper.py 'p, os.stat(p).st_ctime | p[0], datetime.datetime.fromtimestamp(p[1]) | min(pp, key=lambda x:x[1]) | [str(i) for i in p]'

You can wrap it up in a good old bash function, and play with it around::

 oldest_in () { find $1 | pyper.py 'p, os.stat(p).st_ctime | p[0], datetime.datetime.fromtimestamp(p[1]) | min(pp, key=lambda x:x[1]) | [str(i) for i in p]'; }
 oldest_in <that_dir>

If you get exceptions, they are going to standard output. They are not going to
your next unix pipe stage and you can filter them out using ``2> /dev/null``.

Other examples
--------------

The following examples can be ran like the one before. They are written this
way to work also like actual automatic tests.

    >>> from pyper import test
    >>> matrix_ = '''
    ... 234 4 6
    ... 2323 5 2
    ... 6546 7 5
    ... 675
    ... '''
    >>> test('p.split() | p[2] | int(p) - 3', matrix_)
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

    >>> test('p |', 'iterable')
    iterable
    >>> test('p ^', 'iterable')
    i
    t
    e
    r
    a
    b
    l
    e
    >>> test('p.split() ^', 'iter on words')
    iter
    on
    words
    >>> test('p.split() ^ "flattened "+p', matrix_)
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

Reduce
......

    The result of ``&`` is converted to boolean, and it feeds the downstream
    stage just if turns to be True. It doesn't feeds the downstream stage with
    its result (after all, it's just True or False), but with it's original
    ``p`` value.

    >>> test('p.split() ^  2 < int(p) < 10 &', matrix_)
    4
    6
    5
    7
    5
    
    Filter blank lines:

    >>> input_ = '''
    ... 
    ... this matters
    ... 
    ... '''
    >>> test(' p &', input_)
    this matters

    Act like grep:

    >>> input_ = '''
    ... just noise
    ... use it like grep
    ... if you want
    ... '''
    >>> test(' "grep" in p &', input_)
    use it like grep

Complex cases and mixing ``pp`` with ``p``
------------------------------------------

    The pyper pipeline is made up from **generators**. This makes it extremely
    efficient (you can feed it with gigabyte files without taking system
    memory), but it causes some unintuitive behaviour when using ``pp``. ``pp``
    is a generator and it cannot be used directly as a list. You will have to
    convert it to a list before:

    >>> letters = '''a
    ... b
    ... c
    ... d
    ... e
    ... '''
    >>> test('pp[3:-1]', letters)            # This won't work (pp is a generator)
    >>> test('list(pp) | p[2:-1]', letters)  # This will
    ['c', 'd']

    When using ``p`` together with ``pp``, the latter will dominate over the
    number of results, and so the whole expression will be evaluated just one
    time for all input values.

    >>> test('p, p, p + p, list(pp)', letters)
    ('a', 'a', 'aa', ['a', 'b', 'c', 'd', 'e'])
