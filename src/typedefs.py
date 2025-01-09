""""""
from __future__ import annotations

import ast
from typing import Union, List

# If you have ~20-30 possible statement/node types, you can create a big Union.
StatementType = Union[
    ast.Assign,
    ast.FunctionDef,
    ast.Expr,
    ast.Call,
    ast.Return,
    ast.Name,
    ast.Attribute,
    ast.Constant,
    ast.If,
    ast.IfExp,
    ast.UnaryOp,
    ast.BinOp,
    ast.Compare,
    ast.BoolOp,
    ast.Lambda,
    ast.JoinedStr,
    ast.Subscript,
    ast.ClassDef,
    ast.While,
    ast.AugAssign,
    ast.Tuple,
    ast.Dict,
    ast.List,
    ast.Set,
    ast.For,
    ast.Try,
    ast.ExceptHandler,
    ast.ListComp,
    ast.DictComp,
    ast.SetComp,
    ast.Pass
]

#BodyType = List[StatementType]
BodyType = List[
    Union[
        ast.Expr,
        ast.ClassDef,
        ast.FunctionDef,
        ast.For,
        ast.Assign,
        ast.ExceptHandler,
        ast.Return,
        ast.AugAssign,
        ast.If,
        ast.Try
    ]
]

ClsType = Union[ast.ClassDef]

ArgType = Union[
    ast.Name,
    ast.Attribute,
    ast.Lambda,
    ast.BinOp,
    ast.JoinedStr,
    ast.Constant
]

AssignType = Union[
    ast.Assign,
    ast.AugAssign
]

TargetType = Union[
    ast.Attribute,
    ast.Name
]
