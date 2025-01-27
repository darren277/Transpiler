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
        assert str(e) == "Invalid call object - missing func attribute"
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


def test_funcdef_arg():
    from main import Main

    main = Main('')

    import ast

    a = ast.arg(arg='x', annotation=None)
    result = main.process_funcdef_arg(a)
    expected = 'x'
    assert result == expected

    a = ast.arg(arg='x', annotation=ast.Name(id='int', ctx=ast.Load()))
    result = main.process_funcdef_arg(a)
    expected = 'x: int'
    assert result == expected

    a = ast.arg(arg='x', annotation=ast.Name(id='int', ctx=ast.Load()))
    result = main.process_funcdef_arg(a, default=ast.Constant(value=1))
    expected = 'x: int = 1'
    assert result == expected

    main.config.react_app = True
    a = ast.arg(arg='props', annotation=None)
    result = main.process_funcdef_arg(a)
    expected = '{props}'
    assert result == expected


def test_lambda():
    from main import Main

    main = Main('')

    import ast

    # special case for longer lambdas...
    l = ast.Lambda(args=ast.arguments(args=[ast.arg(arg='x', annotation=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()), op=ast.Add(), right=ast.Constant(value=1)))
    result = main.process_lambda(l)
    expected = 'x => x + 1'
    assert result == expected


def test_bin_op():
    from main import Main

    main = Main('')

    import ast

    body = ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()), op=ast.Add(), right=ast.Constant(value=1))
    result = main.process_bin_op(body)
    expected = 'x + 1'
    assert result == expected

    body = ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()), op=ast.Add(), right=ast.BinOp(left=ast.Name(id='y', ctx=ast.Load()), op=ast.Add(), right=ast.Constant(value=1)))
    result = main.process_bin_op(body)
    expected = 'x + (y + 1)'
    assert result == expected

    body = ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()), op=ast.Add(), right=ast.BinOp(left=ast.Name(id='y', ctx=ast.Load()), op=ast.Add(), right=ast.Constant(value=1)))
    result = main.process_bin_op(body, double_and=True)
    expected = 'x && (y + 1)'
    assert result == expected

    body = ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()), op=ast.Add(), right=ast.BinOp(left=ast.Name(id='y', ctx=ast.Load()), op=ast.Add(), right=ast.Constant(value=1)))
    result = main.process_bin_op(body, special_long_lambda_case=True)
    expected = 'x + (y + 1)'
    assert result == expected

    body = ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()), op=ast.FloorDiv(), right=ast.Constant(value=1))
    result = main.process_bin_op(body)
    expected = 'Math.floor(x / 1)'
    assert result == expected

    # if special_long_lambda_case and (op != '+') and (op != '-') and (op != '*') and (op != '/') and (op != '//'):
    body = ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()), op=ast.Pow(), right=ast.Constant(value=1))
    result = main.process_bin_op(body, special_long_lambda_case=True)
    expected = 'x  1'
    assert result == expected


def test_if():
    # e.test == ast.Name
    from main import Main
    main = Main('')
    import ast
    e = ast.If(test=ast.Name(id='x', ctx=ast.Load()), body=[], orelse=[])
    result = main.process_if(e)
    expected = 'if (x) {\n\n} '
    assert result == expected


def test_call():
    from main import Main
    main = Main('')
    import ast
    c = ast.Call(func=ast.Call(func=ast.Name(id='my_func', ctx=ast.Load()), args=[], keywords=[]), args=[], keywords=[])
    result = main.process_call(c)
    expected = 'my_func()()'
    assert result == expected


#     def process_except(self, e: ast.ExceptHandler) -> str:
#         # logger.warn...
#         if e.type:
#             print(f"WARNING: In JS you need to handle specific error types (i.e. {e.type.id}) internally inside the `catch` block.")

def test_except():
    from main import Main
    main = Main('')
    import ast
    e = ast.ExceptHandler(type=ast.Name(id='Exception', ctx=ast.Load()), name='e', body=[])
    result = main.process_except(e)

    # Should print a warning...
    # TODO: How to test that?

    expected = ''
    assert result == expected


def test_try():
    from main import Main
    main = Main('')
    import ast
    t = ast.Try(body=[], handlers=[], orelse=[], finalbody=[])
    result = main.process_try(t)
    expected = 'try {}\ncatch (e) {}'
    assert result == expected

    t = ast.Try(body=[], handlers=[ast.ExceptHandler(type=ast.Name(id='Exception', ctx=ast.Load()), name='e', body=[])], orelse=[], finalbody=[])
    result = main.process_try(t)
    expected = 'try {}\ncatch (e) {}'
    assert result == expected

    # t.orelse...
    t = ast.Try(body=[], handlers=[], orelse=[ast.Expr(value=ast.Call(func=ast.Name(id='console.log', ctx=ast.Load()), args=[ast.Constant(value='Hello, World!')], keywords=[]))], finalbody=[])
    try:
        result = main.process_try(t)
    except Exception as e:
        assert str(e) == "TODO: Implement else block for try/except"
        result = None

    assert result == None


def test_dict_key():
    from main import Main
    main = Main('')
    import ast
    key = ast.Constant(value='x')
    result = main.process_dict_key(key)
    expected = '"x"'
    assert result == expected

    key = ast.Name(id='x', ctx=ast.Load())
    result = main.process_dict_key(key)
    expected = 'x'
    assert result == expected

    key = 'x'
    result = main.process_dict_key(key)
    expected = 'x'
    assert result == expected

    key = ast.Constant(value=1)
    result = main.process_dict_key(key)
    expected = '1'
    assert result == expected


def test_set():
    from main import Main
    main = Main('')
    import ast
    s = ast.Set(elts=[ast.Constant(value=1), ast.Constant(value=2), ast.Constant(value=3)])

    main.config.set_wrapper = '[]'
    main.config.react_app = False

    result = main.process_set(s)
    expected = 'new Set([1,2,3])'
    assert result == expected

    main.config.set_wrapper = '{}'
    main.config.react_app = False

    result = main.process_set(s)
    expected = 'new Set({1,2,3})'
    assert result == expected

    main.config.set_wrapper = ''
    main.config.react_app = True

    result = main.process_set(s)
    expected = '{1,2,3}'
    assert result == expected


def test_for_loop():
    from main import Main
    main = Main('')
    import ast
    f = ast.For(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()), args=[ast.Constant(value=10)], keywords=[]), body=[ast.Expr(value=ast.Call(func=ast.Name(id='console.log', ctx=ast.Load()), args=[ast.Name(id='x', ctx=ast.Load())], keywords=[]))], orelse=[])
    result = main.process_for_loop(f)
    expected = 'for (let x = 0; x < 10; x++) {console.log(x)} '
    assert result == expected

    f = ast.For(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()), args=[ast.Constant(value=10), ast.Constant(value=20)], keywords=[]), body=[ast.Expr(value=ast.Call(func=ast.Name(id='console.log', ctx=ast.Load()), args=[ast.Name(id='x', ctx=ast.Load())], keywords=[]))], orelse=[])
    result = main.process_for_loop(f)
    expected = 'for (let x = 20; x < 10; x++) {console.log(x)} '
    assert result == expected

    f = ast.For(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()), args=[ast.Constant(value=10), ast.Constant(value=20), ast.Constant(value=2)], keywords=[]), body=[ast.Expr(value=ast.Call(func=ast.Name(id='console.log', ctx=ast.Load()), args=[ast.Name(id='x', ctx=ast.Load())], keywords=[]))], orelse=[])
    result = main.process_for_loop(f)
    expected = 'for (let x = 20; x < 10; x+=2) {console.log(x)} '
    assert result == expected


    # if type(_iter) == Constant or len(_iter.args) == 1:
    f = ast.For(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), body=[ast.Expr(value=ast.Call(func=ast.Name(id='console.log', ctx=ast.Load()), args=[ast.Name(id='x', ctx=ast.Load())], keywords=[]))], orelse=[])
    result = main.process_for_loop(f)
    expected = 'for (let x = 0; x < 10; x++) {console.log(x)} '
    assert result == expected

    # if type(_iter) != Constant and _iter.func.id != 'range':
    f = ast.For(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Call(func=ast.Name(id='my_func', ctx=ast.Load()), args=[], keywords=[]), body=[ast.Expr(value=ast.Call(func=ast.Name(id='console.log', ctx=ast.Load()), args=[ast.Name(id='x', ctx=ast.Load())], keywords=[]))], orelse=[])
    try:
        result = main.process_for_loop(f)
    except Exception as e:
        assert str(e) == "NOT YET IMPLEMENTED"
        result = None

    assert result == None


def test_assign():
    from main import Main
    main = Main('')
    import ast

    e = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=1))
    result = main.process_assign(e)
    expected = 'let x = 1'
    assert result == expected

    e = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Call(func=ast.Name(id='my_func', ctx=ast.Load()), args=[], keywords=[]))
    main.defined_functions.append('my_func')
    result = main.process_assign(e)
    expected = 'let x = my_func()'
    assert result == expected

    e = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Call(func=ast.Name(id='ternary', ctx=ast.Load()), args=[ast.Constant(value=True), ast.Constant(value='yes'), ast.Constant(value='no')], keywords=[]))
    result = main.process_assign(e)
    expected = 'let x = true ? "yes" : "no"'
    assert result == expected

    e = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Call(func=ast.Name(id='dict', ctx=ast.Load()), args=[], keywords=[ast.keyword(arg='a', value=ast.Constant(value=1)), ast.keyword(arg='b', value=ast.Constant(value=2))]))
    result = main.process_assign(e)
    expected = 'let x = {a: 1, b: 2}'
    assert result == expected

    # var, const, let
    e = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Call(func=ast.Name(id='var', ctx=ast.Load()), args=[ast.Constant(value=1)], keywords=[]))
    result = main.process_assign(e)
    expected = 'var x = 1'
    assert result == expected

    e = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Call(func=ast.Name(id='const', ctx=ast.Load()), args=[ast.Constant(value=1)], keywords=[]))
    result = main.process_assign(e)
    expected = 'const x = 1'
    assert result == expected

    e = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Call(func=ast.Name(id='let', ctx=ast.Load()), args=[ast.Constant(value=1)], keywords=[]))
    result = main.process_assign(e)
    expected = 'let x = 1'
    assert result == expected

    # IfExp
    e = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.IfExp(test=ast.Constant(value=True), body=ast.Constant(value='yes'), orelse=ast.Constant(value='no')))
    result = main.process_assign(e)
    expected = 'let x = true ? "yes" : "no"'
    assert result == expected

    # Augment (like x //= 2)
    e = ast.AugAssign(target=ast.Name(id='x', ctx=ast.Store()), op=ast.FloorDiv(), value=ast.Constant(value=2))
    result = main.process_assign(e, augment=True)
    expected = 'x = Math.floor(x / 2)'
    assert result == expected

    # this in target...
    e = ast.Assign(targets=[ast.Name(id='this', ctx=ast.Store())], value=ast.Constant(value=1))
    result = main.process_assign(e)
    expected = 'this = 1'
    assert result == expected


def test_assert():
    from main import Main
    main = Main('')
    import ast

    a = ast.Assert(test=ast.Constant(value=True))
    result = main.process_assert(a)
    expected = 'console.assert(true, \'true\')'
    assert result == expected


def test_subscript():
    from main import Main
    main = Main('')
    import ast

    e = ast.Subscript(value=ast.Name(id='x', ctx=ast.Load()), slice=ast.Index(value=ast.Name(id='y', ctx=ast.Load())), ctx=ast.Load())
    result = main.process_subscript(e)
    expected = 'x[y]'
    assert result == expected

    e = ast.Subscript(value=ast.Call(func=ast.Name(id='my_func', ctx=ast.Load()), args=[], keywords=[]), slice=ast.Index(value=ast.Call(func=ast.Name(id='my_func', ctx=ast.Load()), args=[], keywords=[])), ctx=ast.Load())
    result = main.process_subscript(e)
    expected = 'my_func()[my_func()]'
    assert result == expected


def test_return():
    from main import Main
    main = Main('')
    import ast

    r = ast.Return(value=ast.Constant(value=1))
    result = main.process_return(r)
    expected = 'return 1'
    assert result == expected

    r = ast.Return(value=None)
    main.config.debug = True
    result = main.process_return(r)
    expected = 'return '
    assert result == expected

    main.config.wrap_return = ['(', ')']
    r = ast.Return(value=ast.Constant(value=1))
    result = main.process_return(r)
    expected = 'return (1)'
    assert result == expected

    # if type(expr) == Tuple: raise Exception(f"TODO: Return of {str(expr)}")
    r = ast.Return(value=ast.Tuple(elts=[ast.Constant(value=1), ast.Constant(value=2)]))
    try:
        result = main.process_return(r)
    except Exception as e:
        assert str(e) == "TODO: Return of (1, 2)"
        result = None

    assert result == None


def test_thing():
    # UserService.getUsers().then(lambda res: setUsers(res.data)).catch(lambda err: console.log(err))

    setUsers = ast.Lambda(
        args=ast.arguments(
            args=[ast.arg(arg='res', annotation=None)],
            vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        ),
        body=ast.Call(
            func=ast.Name(id='setUsers', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='res', ctx=ast.Load()), attr='data', ctx=ast.Load())],
            keywords=[]
        )
    )

    console_log = ast.Lambda(
        args=ast.arguments(
            args=[ast.arg(arg='err', annotation=None)],
            vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        ),
        body=ast.Call(
            func=ast.Attribute(value=ast.Name(id='console', ctx=ast.Load()), attr='log', ctx=ast.Load()),
            args=[ast.Name(id='err', ctx=ast.Load())],
            keywords=[]
        )
    )

    from main import Main

    main = Main('')

    # UserService.getUsers().then(lambda res: setUsers(res.data)).catch(lambda err: console.log(err))

    result = main.process_attribute_call(
        ast.Call(
            func=ast.Attribute(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Attribute(value=ast.Name(id='UserService', ctx=ast.Load()), attr='getUsers', ctx=ast.Load()),
                            args=[],
                            keywords=[]
                        ),
                        attr='then',
                        ctx=ast.Load()
                    ),
                    args=[setUsers],
                    keywords=[]
                ),
                attr='catch',
                ctx=ast.Load()
            ),
            args=[console_log],
            keywords=[]
        )
    )

    expected = 'UserService.getUsers().then(res => setUsers(res.data)).catch(err => console.log(err))'
    assert result == expected


def test_special_dict():
    from main import Main

    main = Main('')

    import ast

    # { **prev, [name]: value }
    d = ast.Dict(
        keys=[
            ast.Starred(value=ast.Name(id='prev', ctx=ast.Load()), ctx=ast.Load()),
            ast.Subscript(value=ast.Name(id='name', ctx=ast.Load()), slice=ast.Index(value=ast.Name(id='value', ctx=ast.Load())), ctx=ast.Load())
        ],
        values=[
            ast.Constant(value=None),
            ast.Name(id='value', ctx=ast.Load())
        ]
    )
    result = main.process_dict(d)
    expected = '{...prev, [name]: value}'
    assert result == expected


