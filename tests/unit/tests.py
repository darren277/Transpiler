""""""
import ast

from main import Main


def test_binop_statement():
    binop = ast.BinOp(
        left=ast.Constant(value=1),
        op=ast.Add(),
        right=ast.Constant(value=2)
    )
    result = Main('').process_statement(binop)
    assert result == "1 + 2"

test_binop_statement()
