""""""

from main import Main

def test_main():
    main = Main('')
    assert main is not None
    try:
        main.throw('Testing error throwing in main')
    except Exception as e:
        assert e is not None
        assert str(e) == 'Testing error throwing in main'


    main1 = Main('print("Hello, World!")', config_kwargs={'do_print_code': True})

    assert main1 is not None
    assert main1.config.do_print_code == True

    try:
        from config import ASTConfig
        config = ASTConfig(tuples_in_curly_braces=True, tuples_in_square_brackets=True)
    except Exception as e:
        assert str(e) == 'Make up your mind about the tuples!'



def test_react():
    # def useState(initial_value): return initial_value
    # def useEffect(callback, dependencies): callback()
    # def Fragment(*args, **kwargs): pass

    from src.react import useState, useEffect, Fragment

    assert useState(0) == 0
    assert useEffect(lambda: print('Hello, World!'), []) == None
    assert Fragment() == None





def test_logger():
    from src.logger import Logger

    logger = Logger()

    logger.info("This is an info message")
    logger.debug("This is a debug message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")


def test_unindent_line():
    from parsetools import unindent_line
    assert unindent_line('    def test_unindent_line():') == 'def test_unindent_line():'

def test_unindent():
    from parsetools import unindent
    assert unindent('    def test_unindent_line():\n        assert unindent_line("    def test_unindent_line():") == "def test_unindent_line():"') == 'def test_unindent_line():\n    assert unindent_line("    def test_unindent_line():") == "def test_unindent_line():"'

def test_analyze_class():
    from parsetools import analyze_class
    analyze_class(Main)


def test_special_types():
    from special_types import var, let, const, ternary

    assert str(var('x')) == 'var x'
    assert str(let('x')) == 'let x'
    assert str(const('x')) == 'const x'

    assert ternary(1 + 1 == 2, True, False) == True


def test_hooks():
    parser = Main('print("Hello, World!")')

    parser.config.do_print_code = True

    parsed = parser.transpile()

    assert 'console.log("Hello, World!")' in parsed


def test_utils():
    from utils import convert_back_to_code

    import ast

    a = ast.parse('console.log("Hello, World!")')

    _a = a.body
    r = convert_back_to_code('console.log("Hello, World!")', _a)
    assert r == ''

    _a = a.body[0]
    r = convert_back_to_code('console.log("Hello, World!")', _a)
    assert r == 'console.log("Hello, World!")'


    from utils import debug_util

    assert debug_util('console.log("Hello, World!")') == None