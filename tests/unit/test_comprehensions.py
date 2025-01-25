""""""


def test_list_comp():
    from main import Main
    main = Main('')
    import ast

    e = ast.ListComp(elt=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[], is_async=False)])
    result = main.process_list_comp(e)
    expected = '(1 for x in 10)'
    assert result == expected

    # Multiple generators...
    e = ast.ListComp(elt=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[], is_async=False), ast.comprehension(target=ast.Name(id='y', ctx=ast.Store()), iter=ast.Constant(value=20), ifs=[], is_async=False)])
    try:
        result = main.process_list_comp(e)
    except Exception as e:
        assert str(e) == "TODO: Multiple generators in list comprehension..."
        result = None

    assert result == None

    # If statements...
    e = ast.ListComp(elt=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[ast.Constant(value=True)], is_async=False)])
    try:
        result = main.process_list_comp(e)
    except Exception as e:
        assert str(e) == "TODO: If statements in list comprehension..."
        result = None

    assert result == None

    # Async...
    e = ast.ListComp(elt=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[], is_async=True)])
    try:
        result = main.process_list_comp(e)
    except Exception as e:
        assert str(e) == "TODO: Async list comprehension..."
        result = None

    assert result == None


def test_dict_comp():
    from main import Main
    main = Main('')
    import ast

    e = ast.DictComp(key=ast.Constant(value='a'), value=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[], is_async=False)])
    result = main.process_dict_comp(e)
    expected = '{ "a": 1 for x in 10 }'
    assert result == expected

    # Multiple generators...
    e = ast.DictComp(key=ast.Constant(value='a'), value=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[], is_async=False), ast.comprehension(target=ast.Name(id='y', ctx=ast.Store()), iter=ast.Constant(value=20), ifs=[], is_async=False)])
    try:
        result = main.process_dict_comp(e)
    except Exception as e:
        assert str(e) == "TODO: Multiple generators in dict comprehension..."
        result = None

    assert result == None

    # If statements...
    e = ast.DictComp(key=ast.Constant(value='a'), value=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[ast.Constant(value=True)], is_async=False)])
    try:
        result = main.process_dict_comp(e)
    except Exception as e:
        assert str(e) == "TODO: If statements in dict comprehension..."
        result = None

    assert result == None

    # Async...
    e = ast.DictComp(key=ast.Constant(value='a'), value=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[], is_async=True)])
    try:
        result = main.process_dict_comp(e)
    except Exception as e:
        assert str(e) == "TODO: Async dict comprehension..."
        result = None

    assert result == None


def test_set_comp():
    from main import Main
    main = Main('')
    import ast

    e = ast.SetComp(elt=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[], is_async=False)])
    result = main.process_set_comp(e)
    expected = '{ 1 for x in 10 }'
    assert result == expected

    # Multiple generators...
    e = ast.SetComp(elt=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[], is_async=False), ast.comprehension(target=ast.Name(id='y', ctx=ast.Store()), iter=ast.Constant(value=20), ifs=[], is_async=False)])
    try:
        result = main.process_set_comp(e)
    except Exception as e:
        assert str(e) == "TODO: Multiple generators in set comprehension..."
        result = None

    assert result == None

    # If statements...
    e = ast.SetComp(elt=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[ast.Constant(value=True)], is_async=False)])
    try:
        result = main.process_set_comp(e)
    except Exception as e:
        assert str(e) == "TODO: If statements in set comprehension..."
        result = None

    assert result == None

    # Async...
    e = ast.SetComp(elt=ast.Constant(value=1), generators=[ast.comprehension(target=ast.Name(id='x', ctx=ast.Store()), iter=ast.Constant(value=10), ifs=[], is_async=True)])
    try:
        result = main.process_set_comp(e)
    except Exception as e:
        assert str(e) == "TODO: Async set comprehension..."
        result = None

    assert result == None
