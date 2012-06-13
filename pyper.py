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

def reintegrate(p, input):
    '''
    When iterators containing `pp` are created, the first p is already
    consumed. So the iterator defining the whole list must be reintegrated with
    the lost p. In other words, iterators with `pp` can't use `input` directly
    '''
    yield p
    for p in input:
        yield p

def single(expression, input):
    for p in input:
        pp = reintegrate(p, input)
        with exception_handling(expression, p):
            yield eval(expression)
         
def produce(expression, input):
    for p in input:
        pp = reintegrate(p, input)
        with exception_handling(expression, p):
            for e in eval(expression):
                yield e
         
def reduce_(expression, input):
    for p in input:
        pp = reintegrate(p, input)
        with exception_handling(expression, p):
            c = eval(expression)
            if bool(c):
                yield p
         
def process(command, input):
    for stage in parse(command):
        expression, type_ = stage[:-1], stage[-1]
        iterator = {
            '|' : single,
            '^' : produce,
            '&' : reduce_,
        }[type_]
        input = iterator(expression, input)

    for p in input:
        yield p

def main(command, input):
    command = r"p.strip('\n') | " + command.strip()
    if command[-1] not in '|^&': command += '|'
    for p in process(command, input):
        print(p)

def test(command, input_):
    main(command, input_.splitlines())

if __name__=='__main__':
    options, args = OptionParser().parse_args()
    main(args[0], sys.stdin)
