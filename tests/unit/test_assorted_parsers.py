""""""
import ast

from main import Main


def test_process_bool_op():
    main = Main('')

    arg = ast.BoolOp()
    arg.op = ast.And()
    arg.values = [ast.NameConstant(value=True), ast.NameConstant(value=False)]
    expected = 'true && false'
    assert main.process_bool_op(arg) == expected

    arg = ast.BoolOp()
    arg.op = ast.Or()
    arg.values = [ast.NameConstant(value=True), ast.NameConstant(value=False)]
    expected = 'true || false'
    assert main.process_bool_op(arg) == expected

    arg = ast.BoolOp()
    arg.op = ast.And()
    arg.values = [ast.NameConstant(value=True), ast.NameConstant(value=True), ast.NameConstant(value=False)]
    expected = 'true && true && false'
    assert main.process_bool_op(arg) == expected

    arg = ast.BoolOp
    arg.op = ast.Or()
    arg.values = [ast.NameConstant(value=True), ast.NameConstant(value=True), ast.NameConstant(value=False)]
    expected = 'true || true || false'
    assert main.process_bool_op(arg) == expected

    arg = ast.BoolOp()
    arg.op = ast.Or()
    arg.values = [ast.BoolOp(op=ast.And(), values=[ast.NameConstant(value=True), ast.NameConstant(value=False)]), ast.NameConstant(value=True)]
    expected = 'true && false || true'
    assert main.process_bool_op(arg) == expected

