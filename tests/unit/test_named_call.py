""""""
import ast

import jsbeautifier

from main import Main


def assert_beautified(result, expected):
    assert jsbeautifier.beautify(result) == jsbeautifier.beautify(expected)


def test_named_call():
    main = Main('')

    try:
        result = main.process_named_call(ast.Call(func=ast.Name(id='dict', ctx=ast.Load()), args=[], keywords=[]))
    except Exception as e:
        result = str(e)

    expected = "EMPTY DICT???"
    assert result == expected

    try:
        result = main.process_named_call(ast.Call(func=ast.Name(id='dict', ctx=ast.Load()), args=[], keywords=[ast.keyword(arg='key', value=ast.Constant(value='value'))]))
    except Exception as e:
        result = str(e)

    expected = "This should be handled elsewhere for traditional assignments of dict() but this could occur in an edge case to be resolved later."
    assert result == expected


    # super...
    result = main.process_named_call(ast.Call(func=ast.Name(id='super', ctx=ast.Load()), args=[], keywords=[]))
    expected = "super()"

    assert result == expected


    # ternary...
    result = main.process_named_call(ast.Call(func=ast.Name(id='ternary', ctx=ast.Load()), args=[
        ast.Constant(value=True),
        ast.Constant(value='yes'),
        ast.Constant(value='no')
    ], keywords=[]))
    expected = 'true ? "yes" : "no"'

    assert result == expected


    # break ternary (more than 3 args...)
    try:
        result = main.process_named_call(ast.Call(func=ast.Name(id='ternary', ctx=ast.Load()), args=[
            ast.Constant(value=True),
            ast.Constant(value='yes'),
            ast.Constant(value='no'),
            ast.Constant(value='maybe')
        ], keywords=[]))
    except Exception as e:
        result = str(e)

    expected = "Ternary operator must have 3 arguments."
    assert result == expected


    # type...
    result = main.process_named_call(ast.Call(func=ast.Name(id='type', ctx=ast.Load()), args=[
        ast.Constant(value='hello')
    ], keywords=[]))
    expected = 'typeof "hello"'
    print('RESULT:', result)

    assert result == expected


    # print...
    result = main.process_named_call(ast.Call(func=ast.Name(id='print', ctx=ast.Load()), args=[], keywords=[]))
    expected = "console.log()"

    assert result == expected


    # PURE_STRING...
    result = main.process_named_call(ast.Call(func=ast.Name(id='PURE_STRING', ctx=ast.Load()), args=[
        ast.Constant(value='hello')
    ], keywords=[]))
    expected = 'hello'

    assert result == expected


