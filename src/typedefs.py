""""""
from __future__ import annotations

import ast
from typing import Union, List

# If you have ~20-30 possible statement/node types, you can create a big Union.
StatementType = Union[
    ast.BinOp,
    ast.Name,
    ast.FunctionDef,
    ast.Expr,
    ast.Return,
    ast.If,
    ast.For,
    ast.While,
    ast.Constant,
    ast.ClassDef,
    ast.Call,
    # ... etc.
    # (Add all the AST node classes your transpiler needs to handle)
]

#BodyType = List[StatementType]
BodyType = List[Union[ast.Expr, ast.Assign]]

ClsType = Union[ast.ClassDef]
