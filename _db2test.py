from db2 import *
import db2
from random import choice, randint
from traceback import format_exception

def test1():
    comp = ('add', 'sub', 'mul', 'div')
    x = [(choice(comp), randint(1, 20)) for _ in range(randint(2, 10))]
    x.insert(2, None)
    x.insert(0, ('null', 15))
    print(db2._translate_operands(x, None, ('add', 0)))
    return True

def test2():
    x = db2.where('data')
    y = (x == 'data')+2
    print(y)
    return True


if __name__ == '__main__':
    print("\033[7mTest begin\033[0m")
    fnc = (globals()[f'test{a}'] for a in range(0, 100) if f"test{a}" in globals())
    fails = 0
    totals = 0
    for fn in fnc:
        print(f"\033[33mTest on\033[0m \33[34m{fn.__name__}\033[0m")
        try:       
            x = fn()
        except Exception as exc:
            print(f"\033[31mFailed!\033[0m ({type(exc).__name__}): {str(exc)}")
            print(''.join(format_exception(exc, exc, exc.__traceback__)))
            fails += 1
            x = None
        print("\033[32mPass!\033[32m Return value", x, end='\033[0m\n\n') if x is not None else None
        totals += 1
    print(f"\033[7mTest done for {totals} functions, \33[32m{totals-fails}\033[0m\033[7m pass and \33[31m{fails}\33[0m\033[7m fails\033[0m")