""""""
import ast

import jsbeautifier

from main import Main


def assert_beautified(result, expected):
    assert jsbeautifier.beautify(result) == jsbeautifier.beautify(expected)


def test_name_arg():
    arg = ast.Name(id='x')
    result = Main('').process_arg(arg)
    print(result)
    expected = 'x'
    assert_beautified(result, expected)


def test_attribute_arg():
    arg = ast.Attribute(
        value=ast.Name(id='x'),
        attr='y'
    )
    result = Main('').process_arg(arg)
    print(result)
    expected = 'x.y'
    assert_beautified(result, expected)


def test_lambda_arg():
    arg = ast.Lambda(args=ast.arguments(args=[ast.arg(arg='x')]), body=ast.Constant(value=1))
    result = Main('').process_arg(arg)
    print(result)
    expected = 'x => 1'
    assert_beautified(result, expected)


def test_bin_op_arg():
    arg = ast.BinOp(left=ast.Constant(value=1), op=ast.Mult(), right=ast.Constant(value=2))
    result = Main('').process_arg(arg)
    print(result)
    expected = '1 * 2'
    assert_beautified(result, expected)


def test_joined_str_arg():
    arg = ast.JoinedStr(values=[ast.Constant(value='x = '), ast.Name('x'), ast.Constant(value=' and y = '), ast.Name('y')])
    result = Main('').process_arg(arg)
    print(result)
    expected = "`x = ${x} and y = ${y}`"
    assert_beautified(result, expected)


def test_constant_arg():
    arg = ast.Constant(value='x')
    result = Main('').process_arg(arg)
    print(result)
    expected = '"x"'
    assert_beautified(result, expected)


def test_process_bin_op():
    arg = ast.BinOp(left=ast.Constant(value=1), op=ast.Mult(), right=ast.Constant(value=2))
    result = Main('').process_arg(arg)
    expected = '1 * 2'
    assert_beautified(result, expected)

    # type(a.op) != Mult
    arg = ast.BinOp(left=ast.Constant(value=1), op=ast.Add(), right=ast.Constant(value=2))
    result = Main('').process_arg(arg)
    expected = '1 + 2'
    assert_beautified(result, expected)

