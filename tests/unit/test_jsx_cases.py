""""""
import ast

from jsbeautifier import beautify

from main import Main


def test_react_app():
    main = Main('print("Hello, World!")')

    main.config.react_app = True
    main.transpile()

    main.imported_components = ['React', 'Component']
    main.defined_classes = ['App']
    main.defined_functions = ['render']
    assert main.is_already_defined('App') is True
    assert main.is_already_defined('render') is True
    assert main.is_already_defined('React') is True


    #     def is_react_component(self, function_name: str):
    #         return (((function_name.lower == 'Fragment'.lower()) or (function_name.lower() in HTML_TAGS) or self.is_already_defined(function_name)))
    assert main.is_react_component('Fragment') is True


def test_named_call():
    #         if self.inside_return and self.is_react_component(function_name):
    #             # HTML TAG CASE or IMPORTED REACT COMPONENT CASE
    #             close1, close2 = ('/', '') if function_name.lower() in self.imported_components else ('', f'</{function_name}>')
    #             if content:
    #                 actual_contents = [kw.value for kw in kwargs if kw.arg == 'content'][0]
    #                 kwargs_string += ", ".join([f"{kw.arg}={self.process_arg(kw.value)}" for kw in kwargs if not kw.arg == 'content'])
    #                 return f"<{function_name}{kwargs_string.replace(', ', ' ')}{close1}>{self.process_statement(actual_contents)}{close2}"
    #             else:
    #                 kwargs_string += ", ".join([f"{kw.arg}={{{self.process_arg(kw.value)}}}" for kw in kwargs])
    #                 if "True" in kwargs_string:
    #                     kwargs_string = kwargs_string.replace('="True"', '')
    #                 return f"<{function_name}{kwargs_string.replace(', ', ' ')}{close1}>{args_string}{close2}"

    main = Main('''
def App():
    def render():
        return (Fragment(content=Component()))
    ''')

    main.config.react_app = True
    main.config.wrap_return = "()"

    main.imported_components = ['React', 'Component']

    result = main.transpile()

    #assert main.transpiled_code == 'def render():\n    return <Fragment content={Component()}>'

    print('result:', result)

    # TODO: assert result == "import React from 'react';\n\nfunction render() {\n    return <Fragment><Component></Component></Fragment>\n}"


def test_styles():
    s = "def App(): return (div(p('Hello'), style={'display': 'flex', 'gap': '10px', 'marginBottom': '10px'}))"

    main = Main(s)
    main.config.react_app = True
    main.config.wrap_return = "()"

    main.inside_return = True

    result = main.transpile()
    print('result:', result)
    assert beautify(result, opts=dict(e4x=True)) == beautify("""import React from 'react';\n\nfunction App() {return (<div style={{"display": "flex", "gap": "10px", "marginBottom": "10px"}}><p>{"Hello"}</p></div>)}\n\nexport default App;""", opts=dict(e4x=True))



    ...
