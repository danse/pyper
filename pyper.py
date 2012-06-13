#!/usr/bin/python
from __future__ import print_function
import sys
import traceback
from optparse import OptionParser
from contextlib import contextmanager
# for the piped commands
import collections
import datetime
import pprint
import re
import os

def parse(command):
    """
    >>> [p for p in parse('p.split() | p[2] | int(p) - 3 &')]
    ['p.split() |', 'p[2] |', 'int(p) - 3 &']
    >>> [p for p in parse('p.split() | p[2] & int(p) - 3 |')]
    ['p.split() |', 'p[2] &', 'int(p) - 3 |']
    >>> [p for p in parse('p.split() ^ p[2] & int(p) - 3|')]
    ['p.split() ^', 'p[2] &', 'int(p) - 3|']
    """
    while command:
        match = re.search('(.*?[&|^])(.*)', command)
        stage, command = match.group(1).strip(), match.group(2).strip()
        yield stage

@contextmanager
def exception_handling(expression, p):
    try:
        yield
    except:
        traceback.print_exc()
        print('While evaluating {0!r} with p={1!r}'.format(expression, p), file=sys.stderr)

def single(expression, pp):
    for p in pp:
        with exception_handling(expression, p):
            yield eval(expression)
         
def produce(expression, pp):
    for p in pp:
        with exception_handling(expression, p):
            for e in eval(expression):
                yield e
         
def reduce_(expression, pp):
    for p in pp:
        with exception_handling(expression, p):
            c = eval(expression)
            if bool(c):
                yield p
         
def process(command, pp):
    for stage in parse(command):
        expression, type_ = stage[:-1], stage[-1]
        iterator = {
            '|' : single,
            '^' : produce,
            '&' : reduce_,
        }[type_]
        pp = iterator(expression, pp)

    for p in pp:
        yield p

def main(command, pp):
    command = r"p.strip('\n') | " + command.strip()
    if command[-1] not in '|^&': command += '|'
    for p in process(command, pp):
        print(p)

def test(command, input):
    main(command, input.splitlines())

if __name__=='__main__':
    options, args = OptionParser().parse_args()
    main(args[0], sys.stdin)
