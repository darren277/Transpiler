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


def test_parse_import():
    main = Main('')

    main.parse_import("import os")
    assert main.import_lines[0] == 'import "os"'

    main.parse_import("from db import DbController")
    assert main.import_lines[1] == 'import { DbController } from "db"'

    main.parse_import("from settings import *")
    assert main.import_lines[2] == 'import * as settings from "settings"'

    main.parse_import("from db import DbController, DbModel")
    assert main.import_lines[3] == 'import { DbController, DbModel } from "db"'

    i = main.add_other_imports()
    assert i == 'import "os"\nimport { DbController } from "db"\nimport * as settings from "settings"\nimport { DbController, DbModel } from "db"'


