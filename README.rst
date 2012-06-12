micro python piper (forget awk)
===============================

From the genial idea by Toby Rosen, pyp:
http://code.google.com/p/pyp/


How to install::

 $ pip install git+https://github.com/danse/micropyp.git

How to play::

 $ cat test 
 2
 3
 4
 $ micropyp.py ' int(p) | sum(pp) ' < test
 7

A quite contorted example, find the file with the oldest change time in a
directory::

 $ find | micropyp.py 'p, os.stat(p).st_ctime | p[0], datetime.datetime.fromtimestamp(p[1]) | min(pp, key=lambda x:x[1]) | [str(i) for i in p]'

You can wrap it up in a good old bash function, and play with it around::

 $ oldest_in () { find $1 | micropyp.py 'p, os.stat(p).st_ctime | p[0], datetime.datetime.fromtimestamp(p[1]) | min(pp, key=lambda x:x[1]) | [str(i) for i in p]'; }
 $ oldest_in <that_dir>

Other examples
--------------

Following examples can be ran like the one before. They also are actual tests.

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
