""""""
import ast
import jsbeautifier

from main import Main


def assert_beautified(result, expected):
    assert jsbeautifier.beautify(result) == jsbeautifier.beautify(expected)


def test_binop_statement():
    binop = ast.BinOp(
        left=ast.Constant(value=1),
        op=ast.Add(),
        right=ast.Constant(value=2)
    )
    result = Main('').process_statement(binop)
    assert result == "1 + 2"


def test_assign_statement():
    assign = ast.Assign(
        targets=[ast.Name(id='x')],
        value=ast.Constant(value=1)
    )
    result = Main('').process_statement(assign)
    print(result)
    assert_beautified(result, "let x = 1")


def test_functiondef_statement():
    funcdef = ast.FunctionDef(
        name='test',
        args=ast.arguments(args=[], posonlyargs=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
        #body=[ast.Expr(value=ast.Constant(value=1))],
        # return None
        body=[ast.Return(value=ast.Constant(value=1))]
    )
    result = Main('').process_statement(funcdef)
    print(jsbeautifier.beautify(result))
    expected = """
function test () {
    return 1
}
"""
    assert_beautified(result, expected)


def test_expr_statement():
    expr = ast.Expr(value=ast.Constant(value=1))
    result = Main('').process_statement(expr)
    print(result)
    assert_beautified(result, "1")


def test_return_statement():
    ret = ast.Return(value=ast.Constant(value=1))
    result = Main('').process_statement(ret)
    print(result)
    assert_beautified(result, "return 1")


def test_name_statement():
    name = ast.Name(id='x')
    result = Main('').process_statement(name)
    print(result)
    assert_beautified(result, "x")


def test_attribute_statement():
    attribute = ast.Attribute(
        value=ast.Name(id='x'),
        attr='y'
    )
    result = Main('').process_statement(attribute)
    print(result)
    assert_beautified(result, "x.y")


def test_call_statement():
    call = ast.Call(
        func=ast.Name(id='test'),
        args=[ast.Constant(value=1)],
        keywords=[]
    )
    result = Main('').process_statement(call)
    print(result)
    assert_beautified(result, "test(1)")


def test_if_statement():
    if_ = ast.If(
        test=ast.Constant(value=True),
        body=[ast.Expr(value=ast.Constant(value=1))],
        orelse=[]
    )
    result = Main('').process_statement(if_)
    print(result)
    expected = "if (true) {\n    1\n}"
    assert_beautified(result, expected)


def test_ifexp_statement():
    ifexp = ast.IfExp(
        test=ast.Constant(value=True),
        body=ast.Constant(value=1),
        orelse=ast.Constant(value=2)
    )
    result = Main('').process_statement(ifexp)
    print(result)
    assert_beautified(result, "if (true) {\n    1\n} else {\n    2\n}")


def test_unaryop_statement():
    unaryop = ast.UnaryOp(
        op=ast.USub(),
        operand=ast.Constant(value=1)
    )
    result = Main('').process_statement(unaryop)
    print(result)
    assert_beautified(result, "-1")


def test_compare_statement():
    compare = ast.Compare(
        left=ast.Constant(value=1),
        ops=[ast.Eq()],
        comparators=[ast.Constant(value=2)]
    )
    result = Main('').process_statement(compare)
    print(result)
    assert_beautified(result, "1 == 2")


def test_boolop_statement():
    boolop = ast.BoolOp(
        op=ast.And(),
        values=[ast.Constant(value=True), ast.Constant(value=False)]
    )
    result = Main('').process_statement(boolop)
    print(result)
    assert_beautified(result, "true && false")


def test_lambda_statement():
    lambda_ = ast.Lambda(
        args=ast.arguments(args=[ast.arg(arg='x')], posonlyargs=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
        body=ast.Constant(value=1)
    )
    result = Main('').process_statement(lambda_)
    print(result)
    assert_beautified(result, "x => 1")


def test_joinedstr_statement():
    joinedstr = ast.JoinedStr(
        values=[ast.Constant(value='x = '), ast.Name('x'), ast.Constant(value='!')]
    )
    result = Main('').process_statement(joinedstr)
    print(result)
    assert_beautified(result, "`x = ${x}!`")


def test_subscript_statement():
    subscript = ast.Subscript(
        value=ast.Name(id='x'),
        slice=ast.Index(value=ast.Constant(value=1))
    )
    result = Main('').process_statement(subscript)
    print(result)
    assert_beautified(result, "x[1]")


classdef = ast.ClassDef(
    name='Test',
    bases=[],
    keywords=[],
    body=[ast.FunctionDef(
        name='__init__',
        args=ast.arguments(args=[], posonlyargs=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
        body=[ast.Assign(
            targets=[ast.Attribute(
                value=ast.Name(id='self'),
                attr='x'
            )],
            value=ast.Constant(value=1)
        )]
    )]
)

def test_classdef_statement():
    parser = Main('')
    parser.config.react_app = False
    result = parser.process_statement(classdef)
    print(result)
    expected = "class Test {\n    constructor () {\n        this.x = 1\n    }\n}"
    assert_beautified(result, expected)


def test_classdef_statement_react():
    parser = Main('')
    parser.config.react_app = True
    result = parser.process_statement(classdef)
    print(result)
    expected = "class Test {\n    constructor (props) {\n        super(props)\n        this.x = 1\n    }\n}"
    assert_beautified(result, expected)


def test_while_statement():
    while_ = ast.While(
        test=ast.Constant(value=True),
        body=[ast.Expr(value=ast.Constant(value=1))],
        orelse=[]
    )
    result = Main('').process_statement(while_)
    print(result)
    expected = "while (true) {\n    1\n}"
    assert_beautified(result, expected)


def test_augassign_statement():
    augassign = ast.AugAssign(
        target=ast.Name(id='x'),
        op=ast.Add(),
        value=ast.Constant(value=1)
    )
    result = Main('').process_statement(augassign)
    print(result)
    assert_beautified(result, "x += 1")


def test_tuple_statement():
    tuple_ = ast.Tuple(
        elts=[ast.Constant(value=1), ast.Constant(value=2)]
    )
    result = Main('').process_statement(tuple_)
    print(result)
    assert_beautified(result, "[1, 2]")


def test_dict_statement():
    dict_ = ast.Dict(
        keys=[ast.Constant(value=1), ast.Constant(value=2)],
        values=[ast.Constant(value=3), ast.Constant(value=4)]
    )
    result = Main('').process_statement(dict_)
    print(jsbeautifier.beautify(result))
    assert_beautified(result, "{1: 3, 2: 4}")


def test_list_statement():
    list_ = ast.List(
        elts=[ast.Constant(value=1), ast.Constant(value=2)]
    )
    result = Main('').process_statement(list_)
    print(result)
    assert_beautified(result, "[1, 2]")


def test_set_statement():
    set_ = ast.Set(
        elts=[ast.Constant(value=1), ast.Constant(value=2)]
    )
    parser = Main('')
    parser.config.react_app = False
    result = parser.process_statement(set_)
    print(result)
    assert_beautified(result, "new Set([1, 2])")


def test_set_statement_react():
    set_ = ast.Set(
        elts=[ast.Constant(value=1), ast.Constant(value=2)]
    )
    parser = Main('')
    parser.config.react_app = True
    result = parser.process_statement(set_)
    print(result)
    assert_beautified(result, "{1, 2}")


def test_for_statement():
    # for (let x = 0; x < 10; x++) {}
    for_ = ast.For(
        target=ast.Name(id='x'),
        iter=ast.Constant(value=10),
        body=[ast.Expr(value=ast.Constant(value=1))],
        orelse=[]
    )
    result = Main('').process_statement(for_)
    print(result)
    expected = "for (let x = 0; x < 10; x++) {\n    1\n}"
    assert_beautified(result, expected)


def test_try_statement():
    try_ = ast.Try(
        body=[ast.Expr(value=ast.Constant(value=1))],
        handlers=[ast.ExceptHandler(
            type=None,
            name=None,
            body=[ast.Expr(value=ast.Constant(value=2))]
        )],
        orelse=[],
        finalbody=[]
    )
    result = Main('').process_statement(try_)
    print(result)
    expected = "try {\n    1\n} catch (e) {\n    2\n}"
    assert_beautified(result, expected)


def test_excepthandler_statement():
    excepthandler = ast.ExceptHandler(
        type=None,
        name=None,
        body=[ast.Expr(value=ast.Constant(value=1))]
    )
    result = Main('').process_statement(excepthandler)
    print(result)
    assert_beautified(result, "1")


def test_pass_statement():
    pass_ = ast.Pass()
    result = Main('').process_statement(pass_)
    print(result)
    assert result == ""
