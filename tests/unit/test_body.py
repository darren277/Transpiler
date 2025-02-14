""""""
import ast

import jsbeautifier

from main import Main


def assert_beautified(result, expected):
    assert jsbeautifier.beautify(result) == jsbeautifier.beautify(expected)


def test_expr_body():
    body = [ast.Expr(value=ast.Constant(value=1))]
    result = Main('').process_body(body)
    print(result)
    assert result == "1\n"


def test_class_body():
    body = [ast.ClassDef(name='MyClass', bases=[], keywords=[], body=[], decorator_list=[])]
    result = Main('').process_body(body)
    print(result)
    expected = "class MyClass {\n}\n"
    assert_beautified(result, expected)


def test_function_body():
    body = [ast.FunctionDef(name='my_function', args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[], decorator_list=[])]
    result = Main('').process_body(body)
    print(result)
    expected = "function my_function() {\n}\n"
    assert_beautified(result, expected)


def test_for_body():
    body = [ast.For(target=ast.Name(id='i'), iter=ast.Constant(value=10), body=[])]
    result = Main('').process_body(body)
    print(result)
    expected = "for (let i = 0; i < 10; i++) {\n}\n"
    assert_beautified(result, expected)


def test_assign_body():
    body = [ast.Assign(targets=[ast.Name(id='x')], value=ast.Constant(value=1))]
    result = Main('').process_body(body)
    print(result)
    expected =  "let x = 1\n"
    assert_beautified(result, expected)


def test_except_body():
    body = [ast.ExceptHandler(type=None, name=None, body=[])]
    result = Main('').process_body(body)
    print(result)
    # NOTE: Why does this return an empty string?
    # Currently, that is by design, as the `process_try()` function is what adds the `catch` block.
    # This makes sense because you would never have a `catch` block without a `try` block.
    #expected = "catch {\n}\n"
    expected = ""
    assert_beautified(result, expected)


def test_return_body():
    body = [ast.Return(value=ast.Constant(value=1))]
    m = Main('')
    m.config.wrap_return = ""
    result = m.process_body(body)
    print(result)
    expected = "return 1\n"
    assert_beautified(result, expected)


def test_augassign_body():
    body = [ast.AugAssign(target=ast.Name(id='x'), op=ast.Add(), value=ast.Constant(value=1))]
    result = Main('').process_body(body)
    print(result)
    expected = "x += 1\n"
    assert_beautified(result, expected)


def test_if_body():
    body = [ast.If(test=ast.Constant(value=True), body=[], orelse=[])]
    result = Main('').process_body(body)
    print(result)
    expected = "if (true) {\n\n}\n"
    assert_beautified(result, expected)


def test_try_body():
    body = [ast.Try(body=[], handlers=[], orelse=[], finalbody=[
        ast.Expr(value=ast.Constant(value=1))
    ])]
    result = Main('').process_body(body)
    print(result)
    expected = "try {\n}\ncatch (e) {\n}\nfinally {\n1\n}\n"
    print(expected)
    assert_beautified(result, expected)

