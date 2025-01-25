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


def test_more():
    main = Main('print("Hello, World!")')

    main.transpile(linting_options=dict(test=True))


def test_bool_op():
    from main import Main

    main = Main('')

    import ast
    arg = ast.BoolOp(op=ast.And(), values=[ast.NameConstant(value=True), ast.NameConstant(value=False)])
    result = main.process_bool_op(arg)
    expected = 'true && false'
    assert result == expected


    # OR, AND, NOT

    arg = ast.BoolOp(op=ast.Or(), values=[ast.NameConstant(value=True), ast.NameConstant(value=False)])
    result = main.process_bool_op(arg)
    expected = 'true || false'
    assert result == expected

    arg = ast.BoolOp(op=ast.Not(), values=[ast.NameConstant(value=True)])
    result = main.process_bool_op(arg)
    print('result.....', result)
    expected = '!true'
    assert result == expected


def test_attribute():
    from main import Main

    main = Main('')

    import ast
    # value == Call
    arg = ast.Attribute(value=ast.Call(func=ast.Name(id='my_func', ctx=ast.Load()), args=[], keywords=[]), attr='log', ctx=ast.Load())
    result = main.process_attribute(arg)
    expected = 'my_func()'
    assert result == expected


def test_chained_call():
    from main import Main

    main = Main('')

    import ast
    arg = ast.Call(func=ast.Name(id='my_func', ctx=ast.Load()), args=[], keywords=[])
    result = main.process_chained_call(arg)
    expected = 'my_func()'
    assert result == expected


def test_attribute_call():
    from main import Main

    main = Main('')

    import ast

    try:
        arg = ast.Constant(value='Hello, World!')
        result = main.process_attribute_call(arg)
    except Exception as e:
        assert str(e) == "You're passing something in that is not an actual call... check your if else chain directly below..."
        result = None

    assert result == None


def test_cls():
    from main import Main

    main = Main('')

    import ast

    cls = ast.ClassDef(name='MyClass', bases=[], keywords=[], body=[])
    result = main.process_cls(cls)
    expected = 'class MyClass {}'
    assert result == expected


    cls = ast.ClassDef(name='MyClass', bases=[ast.Name(id='MyBase', ctx=ast.Load()), ast.Name(id='MySecondBase', ctx=ast.Load())], keywords=[], body=[])

    try:
        result = main.process_cls(cls)
    except Exception as e:
        assert str(e) == "JS does not handle multiple inheritence like this. You must define a mixin yourself."
        result = None

    assert result == None


    cls = ast.ClassDef(name='MyClass', bases=[ast.Attribute(value=ast.Name(id='MyBase', ctx=ast.Load()), attr='log', ctx=ast.Load())], keywords=[], body=[])
    result = main.process_cls(cls)
    expected = 'class MyClass extends MyBase.log {}'
    assert result == expected

    cls = ast.ClassDef(name='MyClass', bases=[ast.Attribute(value=ast.Name(id='MyBase', ctx=ast.Load()), attr='log', ctx=ast.Load())], keywords=[], body=[ast.FunctionDef(name='__init__', args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[], decorator_list=[])])
    result = main.process_cls(cls)
    expected = 'class MyClass extends MyBase.log {constructor () {  }}'
    assert result == expected
