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
        if args:
            first_arg_id, args_string = self._process_named_call_args(function_name, args)
        else:
            first_arg_id, args_string = None, ''


        kwargs = call.keywords
        if first_arg_id == 'dict':
            kwargs.extend(args[0].keywords)
        kwargs_string = ''
        if kwargs and not [kw.arg for kw in kwargs if kw.arg == 'content']:
            kwargs_string += ', '

        if self.inside_return and self.is_react_component(function_name):
            return self._render_jsx_component(function_name, kwargs, content, args_string, kwargs_string)
        else:
            return f"{function_name}({args_string}{kwargs_string})"

    def _process_named_call_args(self, function_name: str, args: list) -> tuple:
        if type(args[0]) == Call:
            try:
                first_arg_id = args[0].func.value.id if type(args[0].func) == Attribute else args[0].func.id
            except:
                first_arg_id = None
        sep, wrap_string = ("", True) if (self.inside_return or self.direct_parent[1] == 'render') and self.is_react_component(function_name) else (", ", False)

        # In case you want to do the <></> syntax for React fragments...
        if function_name == 'Fragment':
            return f"<>{''.join([self.process_arg(arg, wrap_string=wrap_string) for arg in args])}</>"

        args_string = sep.join([self.process_arg(arg, wrap_string=wrap_string) for arg in args[1:]]) if first_arg_id == 'dict' else sep.join([self.process_arg(arg, wrap_string=wrap_string) for arg in args])

        return first_arg_id, args_string

    def _render_jsx_component(self, function_name: str, kwargs: list, content, args_string, kwargs_string) -> str:
        """
        Renders a JSX component with appropriate formatting.

        Args:
            function_name: Name of the component or HTML tag
            kwargs: List of keyword arguments
            content: Component content if available
            args_string: String representation of positional arguments
            kwargs_string: String representation of keyword arguments

        Returns:
            Rendered JSX component as a string
        """
        # Determine tag structure based on component type
        is_imported = function_name.lower() in self.imported_components
        tag_end = '/' if is_imported else ''
        closing_tag = '' if is_imported else f'</{function_name}>'

        # Initialize style property
        style_prop = ''

        if content:
            # --- WITH CONTENT CASE ---

            # Extract content from kwargs
            actual_content = [kw.value for kw in kwargs if kw.arg == 'content'][0]

            # Process style if present
            if 'style' in [kw.arg for kw in kwargs]:
                style_value = [kw.value for kw in kwargs if kw.arg == 'style'][0]
                style_prop = f" style={{{self.process_val(style_value, style=True)}}}"

            # Process other props (excluding content and style)
            other_props = [
                f"{kw.arg}={self.process_val(kw.value, style=True if kw.arg == 'style' else False)}"
                for kw in kwargs if kw.arg != 'content' and kw.arg != 'style'
            ]

            # Add props to kwargs_string
            if other_props:
                kwargs_string += ", ".join(other_props)

            # Process content
            rendered_content = self.process_statement(actual_content)
        else:
            # --- WITHOUT CONTENT CASE ---

            # Process props (excluding style)
            props = [
                f"{kw.arg}={{{self.process_val(kw.value)}}}"
                for kw in kwargs if kw.arg != 'style'
            ]

            # Add props to kwargs_string
            if props:
                kwargs_string += ", ".join(props)

            # Process style if present
            if 'style' in [kw.arg for kw in kwargs]:
                style_value = [kw.value for kw in kwargs if kw.arg == 'style'][0]
                style_prop = f" style={{{self.process_val(style_value, style=True)}}}"

            # Use args_string as content
            rendered_content = args_string

        # Handle boolean props
        props_string = kwargs_string
        if "True" in props_string or '{true}' in props_string:
            props_string = props_string.replace('="True"', '').replace('={true}', '')

        # Format props spacing for JSX
        props_string = props_string.replace(', ', ' ')
        if props_string.endswith(' '):
            props_string = props_string[:-1]

        # Construct the final component
        return f"<{function_name}{style_prop}{props_string}{tag_end}>{rendered_content}{closing_tag}"

