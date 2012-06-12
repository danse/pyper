#!/usr/bin/python
from __future__ import print_function
import sys
import traceback
from optparse import OptionParser
# for the piped commands
import re
import os
import datetime

def parse(pipe):
    """
    >>> parse('p.split() | p[2] | int(p) - 3')
    ['p.split()', 'p[2]', 'int(p) - 3']
    """
    return [s.strip() for s in pipe.split('|')]

def stage(command, pp):
    for p in pp:
        try:
            yield eval(command)
        except:
            traceback.print_exc()
            print('While evaluating {0!r} with p={1!r}'.format(command, p), file=sys.stderr)
         
def process(arg, input):
    gen = stage(r"p.strip('\n')", input)
    for command in parse(arg):
        gen = stage(command, gen)

    for p in gen:
        yield p

def main(arg, input):
    for p in process(arg, input):
        print(p)

def test(arg, input):
    main(arg, input.splitlines())

if __name__=='__main__':
    options, args = OptionParser().parse_args()
    main(args[0], sys.stdin)
