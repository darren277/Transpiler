""""""
from _ast import *
import functools


def return_func(func):
    @functools.wraps(func)
    def decorate(self, r):
        self.inside_return = True
        ret = func(self, r)
        self.inside_return = False
        return ret
    return decorate

def pre_hook_wrapper(func):
    @functools.wraps(func)
    def decorate(self, *args, **kwargs):
        self.pre_hook(loc=locals())
        ret = func(self, *args, **kwargs)
        return ret
    return decorate

def post_hook_wrapper(func):
    @functools.wraps(func)
    def decorate(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        self.post_hook(loc=locals())
        return ret
    return decorate


def convert_back_to_code(src: str, a):
    if type(a) == list:
        return ""
    print(a.lineno, a.col_offset, a.end_lineno, a.end_col_offset)
    s = src.splitlines()[a.lineno-1][a.col_offset:a.end_col_offset]
    print(s)
    return s


operators = {
    BitOr: '|',
    BitAnd: '&',
    Sub: '-',
    Div: '/',
    Mult: '*',
    Add: '+',
    Mod: '%'
}

compare_ops = {
    Eq: '==',
    NotEq: '!=',
    Gt: '>',
    GtE: '>=',
    Lt: '<',
    Is: '==='
}

OR = '||'
NOT = 'not'

NEW_LINE = "\n"
N, AND = '\n', '&&'


## TODO: Dealing with '==' vs '==='...



def debug_util(node):
    ...



