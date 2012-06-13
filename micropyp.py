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
    >>> [p for p in parse('p.split() | p[2] | int(p) - 3 &')]
    ['p.split() |', 'p[2] |', 'int(p) - 3 &']
    >>> [p for p in parse('p.split() | p[2] & int(p) - 3 |')]
    ['p.split() |', 'p[2] &', 'int(p) - 3 |']
    >>> [p for p in parse('p.split() ^ p[2] & int(p) - 3|')]
    ['p.split() ^', 'p[2] &', 'int(p) - 3|']
    """
    while pipe:
        match = re.search('(.*?[&|^])(.*)', pipe)
        stage, pipe = match.group(1).strip(), match.group(2).strip()
        yield stage

def single(command, pp):
    for p in pp:
        try:
            yield eval(command)
        except:
            traceback.print_exc()
            print('While evaluating {0!r} with p={1!r}'.format(command, p), file=sys.stderr)
         
def multiple(command, pp):
    for p in pp:
        try:
            for e in eval(command):
                yield e
        except:
            traceback.print_exc()
            print('While evaluating {0!r} with p={1!r}'.format(command, p), file=sys.stderr)
         
def condition(command, pp):
    for p in pp:
        try:
            c = bool(eval(command))
            if c:
                yield p
        except:
            traceback.print_exc()
            print('While evaluating {0!r} with p={1!r}'.format(command, p), file=sys.stderr)
         
def process(arg, input):
    gen = single(r"p.strip('\n')", input)
    for command in parse(arg):
        command, type_ = command[:-1], command[-1]
        stage = {
            '|' : single,
            '^' : multiple,
            '&' : condition,
        }[type_]
        gen = stage(command, gen)

    for p in gen:
        yield p

def main(arg, input):
    arg = arg.strip()
    if arg[-1] not in '|^&': arg = arg + '|'
    for p in process(arg, input):
        print(p)

def test(arg, input):
    main(arg, input.splitlines())

if __name__=='__main__':
    options, args = OptionParser().parse_args()
    main(args[0], sys.stdin)
