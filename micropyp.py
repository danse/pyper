
def parse(pipe):
    """
    >>> parse('p.split() | p[2] | int(p) - 3')
    ['p.split()', 'p[2]', 'int(p) -3']
    """
    return [s.strip() for s in pipe.split('|')]

def stage(command, input):
    for p in input:
        yield eval(command)
         
arg = 'p.split() | p[2] | int(p) - 3'
input = (
'234 4 6',
'2323 5 2',
'6546 7 5',
)

gen = input
for command in parse(arg):
    gen = stage(command, gen)

for p in gen:
    print(p)

