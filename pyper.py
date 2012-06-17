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
    except Exception as e:
        print('Exception "{0}" while evaluating {1!r} with p={2!r}'.format(e, expression, p), file=sys.stderr)

def reintegrate(p, input_):
    '''
    When iterators containing `pp` are created, the first p is already
    consumed. So the iterator defining the whole list must be reintegrated with
    the lost p. In other words, iterators with `pp` can't use `input_` directly
    '''
    yield p
    for p in input_:
        yield p

def single(code, expression, input_):
    for p in input_:
        pp = reintegrate(p, input_)
        with exception_handling(expression, p):
            yield eval(code)
         
def produce(code, expression, input_):
    for p in input_:
        pp = reintegrate(p, input_)
        with exception_handling(expression, p):
            for e in eval(code):
                yield e
         
def reduce_(code, expression, input_):
    for p in input_:
        pp = reintegrate(p, input_)
        with exception_handling(expression, p):
            c = eval(code)
            if bool(c):
                yield p
         
def main(command, input_):
    command = r"p.strip('\n') | " + command.strip()
    if command[-1] not in '|^&': command += '|'

    for stage in parse(command):
        expression, type_ = stage[:-1], stage[-1]
        iterator = {
            '|' : single,
            '^' : produce,
            '&' : reduce_,
        }[type_]
        code   = compile(expression, '<dynamic>', 'eval')
        input_ = iterator(code, expression, input_)

    for p in input_:
        print(p)

def test(command, input_):
    main(command, input_.splitlines())

if __name__=='__main__':
    parser = OptionParser('usage: %prog <command>')
    options, args = parser.parse_args()
    if len(args) < 1:
        parser.error('Hey, you should tell at least what to do on your input!')
    main(args[0], sys.stdin)
