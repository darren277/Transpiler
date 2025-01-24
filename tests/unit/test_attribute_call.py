""""""
import ast

from main import Main


def test_process_attribute_call():
    m = Main('')
    call = ast.Call(func=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='func', ctx=ast.Load()), args=[], keywords=[])
    s = m.process_attribute_call(call)
    assert s == "this.func()"

    # Name
    call = ast.Call(func=ast.Attribute(value=ast.Name(id='calculator', ctx=ast.Load()), attr='add_numbers', ctx=ast.Load()), args=[], keywords=[])
    s = m.process_attribute_call(call)
    assert s == "calculator.add_numbers()"

    # JoinedStr
    call = ast.Call(func=ast.Attribute(value=ast.JoinedStr(values=[ast.Str(s='this is a test')]), attr='split', ctx=ast.Load()), args=[], keywords=[])
    s = m.process_attribute_call(call)
    assert s == "`this is a test`.split()"

    # Attribute
    call = ast.Call(func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='room', ctx=ast.Load()), attr='participants', ctx=ast.Load()), attr='notify', ctx=ast.Load()), args=[], keywords=[])
    s = m.process_attribute_call(call)
    assert s == "room.participants.notify()"

    # Subscript
    call = ast.Call(func=ast.Attribute(value=ast.Subscript(value=ast.Name(id='calculator', ctx=ast.Load()), slice=ast.Index(value=ast.Str(s='arithmetic_functions')), ctx=ast.Load()), attr='add_numbers', ctx=ast.Load()), args=[], keywords=[])
    s = m.process_attribute_call(call)
    assert s == 'calculator["arithmetic_functions"].add_numbers()'

    # List
    call = ast.Call(func=ast.Attribute(value=ast.List(elts=[ast.Str(s='this is a test')], ctx=ast.Load()), attr='append', ctx=ast.Load()), args=[], keywords=[])
    s = m.process_attribute_call(call)
    assert s == '["this is a test"].append()'




