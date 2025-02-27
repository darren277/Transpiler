""""""
import ast
from ast import *

N = '\n'


class NamedCallVisitor:
    def _process_named_call(self, call: ast.Call) -> str:
        # FOR DEBUG PURPOSE, PRINT CONTENT OF PYTHON CODE AS A STRING...
        if self.config.debug:
            print("---------- START OF FUNCTION CALL ----------")
            if type(call.func) == ast.Name:
                print(call.func.id, call.args)
            elif type(call.func) == ast.Attribute:
                print(call.func.value, call.func.attr, call.args)
            print(self.current_code_context)
            print("---------- END OF FUNCTION CALL ----------")
        ## TODO: REFACTOR THIS... ##
        content = False
        if type(call.func) == Call:
            args = N.join([self.process_arg(arg) for arg in call.args])
            return f"{self.process_call(call.func).rstrip()}({args})"
        else:
            try:
                function_name = call.func.id
            except:
                function_name = call.func.attr
        if function_name == 'dict':
            print("DICT CASE!!")
            try:
                print("KEYWORDS:", call.keywords[0].arg, call.keywords[0].value)
                raise Exception("This should be handled elsewhere for traditional assignments of dict() but this could occur in an edge case to be resolved later.")
            except IndexError:
                raise Exception("EMPTY DICT???")

        if function_name == 'super':
            return f"super({', '.join([self.process_arg(arg) for arg in call.args])})"

        if function_name == 'ternary':
            return self.process_ternary(*call.args)

        if function_name == 'type':
            return f'typeof {self.process_arg(call.args[0])}'

        if function_name == 'print':
            return f"console.log({', '.join([self.process_arg(arg) for arg in call.args])})"

        if function_name == 'PURE_STRING':
            return call.args[0].value

        if function_name == 'export_default':
            self.default_export = True
            return f"export default {self.process_arg(call.args[0])}"

        if function_name == 'input_':
            call.func.id = 'input'
            function_name = 'input'

        args = call.args
        args_string = ''
        first_arg_id = None
        if args:
            if type(args[0]) == Call:
                try:
                    first_arg_id = args[0].func.value.id if type(args[0].func) == Attribute else args[0].func.id
                except:
                    first_arg_id = None
            sep, wrap_string = ("", True) if (self.inside_return or self.direct_parent[1] == 'render') and self.is_react_component(function_name) else (", ", False)

            # In case you want to do the <></> syntax for React fragments...
            if function_name == 'Fragment':
                return f"<>{''.join([self.process_arg(arg, wrap_string=wrap_string) for arg in args])}</>"

            args_string += sep.join([self.process_arg(arg, wrap_string=wrap_string) for arg in args[1:]]) if first_arg_id == 'dict' else sep.join([self.process_arg(arg, wrap_string=wrap_string) for arg in args])

        kwargs = call.keywords
        if first_arg_id == 'dict':
            kwargs.extend(args[0].keywords)
        kwargs_string = ''
        if kwargs and not [kw.arg for kw in kwargs if kw.arg == 'content']:
            kwargs_string += ', '

        if self.inside_return and self.is_react_component(function_name):
            # HTML TAG CASE or IMPORTED REACT COMPONENT CASE
            close1, close2 = ('/', '') if function_name.lower() in self.imported_components else (
            '', f'</{function_name}>')

            # Special scenario for the `style` keyword argument...

            style = ''

            if content:
                actual_contents = [kw.value for kw in kwargs if kw.arg == 'content'][0]
                if 'style' in [kw.arg for kw in kwargs]: style = f" style={{{self.process_val([kw.value for kw in kwargs if kw.arg == 'style'][0], style=True)}}}"
                kwargs_string += ", ".join([f"{kw.arg}={self.process_val(kw.value, style=True if kw.arg == 'style' else False)}" for kw in kwargs if not kw.arg == 'content' and kw.arg != 'style'])
                if "True" in kwargs_string or '{true}' in kwargs_string: kwargs_string = kwargs_string.replace( '="True"', '').replace('={true}', '')
                kw_string = kwargs_string.replace(', ', ' ')
                if kw_string.endswith(' '): kw_string = kw_string[:-1]
                return f"<{function_name}{style}{kw_string}{close1}>{self.process_statement(actual_contents)}{close2}"
            else:
                kwargs_string += ", ".join([f"{kw.arg}={{{self.process_val(kw.value)}}}" for kw in kwargs if kw.arg != 'style'])
                if 'style' in [kw.arg for kw in kwargs]: style = f" style={{{self.process_val([kw.value for kw in kwargs if kw.arg == 'style'][0], style=True)}}}"
                if "True" in kwargs_string or '{true}' in kwargs_string: kwargs_string = kwargs_string.replace('="True"', '').replace('={true}', '')
                kw_string = kwargs_string.replace(', ', ' ')
                if kw_string.endswith(' '): kw_string = kw_string[:-1]
                return f"<{function_name}{style}{kw_string}{close1}>{args_string}{close2}"
        else:
            return f"{function_name}({args_string}{kwargs_string})"

