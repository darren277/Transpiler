""""""
import ast
from ast import *
from typing import Optional

N = '\n'


class NamedCallVisitor:
    def _process_named_call(self, call: ast.Call) -> str:
        """
        Process a named function call, handling special cases and JSX components.

        Args:
            call: AST Call node to process

        Returns:
            str: Processed function call as a string
        """
        # Debug logging if enabled
        self._debug_log_function_call(call)

        # Handle recursive function calls
        if isinstance(call.func, Call):
            processed_args = ", ".join([self.process_arg(arg) for arg in call.args])
            return f"{self.process_call(call.func).rstrip()}({processed_args})"

        # Extract function name
        function_name = self._extract_function_name(call)

        # Handle special function cases
        special_result = self._handle_special_function(function_name, call)
        if special_result is not None:
            return special_result

        # Process arguments and keywords
        content = False
        args = call.args
        kwargs = call.keywords

        # Process argument list
        if args:
            first_arg_id, args_string = self._process_named_call_args(function_name, args)

            # Handle dict case
            if first_arg_id == 'dict':
                kwargs.extend(args[0].keywords)
        else:
            first_arg_id, args_string = None, ''

        # Format kwargs string
        kwargs_string = ''
        if kwargs and not any(kw.arg == 'content' for kw in kwargs):
            kwargs_string += ', '

        # Render JSX or regular function call
        if self.inside_return and self.is_react_component(function_name):
            return self._render_jsx_component(function_name, kwargs, content, args_string, kwargs_string)
        else:
            return f"{function_name}({args_string}{kwargs_string})"

    def _debug_log_function_call(self, call: ast.Call) -> None:
        """
        Log function call details for debugging if debug mode is enabled.

        Args:
            call: AST Call node to log
        """
        if not self.config.debug:
            return

        print("---------- START OF FUNCTION CALL ----------")
        if isinstance(call.func, ast.Name):
            print(call.func.id, call.args)
        elif isinstance(call.func, ast.Attribute):
            print(call.func.value, call.func.attr, call.args)
        print(self.current_code_context)
        print("---------- END OF FUNCTION CALL ----------")

    def _extract_function_name(self, call: ast.Call) -> str:
        """
        Extract the function name from a Call node.

        Args:
            call: AST Call node

        Returns:
            str: Function name
        """
        try:
            if isinstance(call.func, ast.Name):
                return call.func.id
            elif isinstance(call.func, ast.Attribute):
                return call.func.attr
            else:
                return "unknown_function"  # Fallback for unexpected types
        except AttributeError:
            return "unknown_function"

    def _handle_special_function(self, function_name: str, call: ast.Call) -> Optional[str]:
        """
        Handle special function cases with custom processing.

        Args:
            function_name: Name of the function
            call: AST Call node

        Returns:
            Optional[str]: Processed string if special case, None otherwise
        """
        # Dictionary of special function handlers
        handlers = {
            'dict': self._handle_dict_function,
            'super': self._handle_super_function,
            'ternary': self._handle_ternary_function,
            'type': self._handle_type_function,
            'print': self._handle_print_function,
            'PURE_STRING': self._handle_pure_string_function,
            'export_default': self._handle_export_default_function,
            'input_': self._handle_input_function
        }

        # Call the handler if function_name is in the handlers dictionary
        handler = handlers.get(function_name)
        if handler:
            return handler(call)

        return None

    def _handle_dict_function(self, call: ast.Call) -> str:
        """Handle the dict() function call."""
        print("DICT CASE!!")
        try:
            print("KEYWORDS:", call.keywords[0].arg, call.keywords[0].value)
            raise Exception(
                "This should be handled elsewhere for traditional assignments of dict() but this could occur in an edge case to be resolved later.")
        except IndexError:
            raise Exception("EMPTY DICT???")

    def _handle_super_function(self, call: ast.Call) -> str:
        """Handle the super() function call."""
        args_str = ', '.join([self.process_arg(arg) for arg in call.args])
        return f"super({args_str})"

    def _handle_ternary_function(self, call: ast.Call) -> str:
        """Handle the ternary() function call."""
        return self.process_ternary(*call.args)

    def _handle_type_function(self, call: ast.Call) -> str:
        """Handle the type() function call."""
        return f'typeof {self.process_arg(call.args[0])}'

    def _handle_print_function(self, call: ast.Call) -> str:
        """Handle the print() function call."""
        args_str = ', '.join([self.process_arg(arg) for arg in call.args])
        return f"console.log({args_str})"

    def _handle_pure_string_function(self, call: ast.Call) -> str:
        """Handle the PURE_STRING() function call."""
        return call.args[0].value

    def _handle_export_default_function(self, call: ast.Call) -> str:
        """Handle the export_default() function call."""
        self.default_export = True
        return f"export default {self.process_arg(call.args[0])}"

    def _handle_input_function(self, call: ast.Call) -> None:
        """Handle the input_() function call."""
        call.func.id = 'input'
        # Return None to continue processing with modified call object
        return None

    def _process_named_call_args(self, function_name: str, args: list) -> tuple:
        """
        Processes arguments for a named function call, handling special cases for React components.

        Args:
            function_name: Name of the function being called
            args: List of arguments to process

        Returns:
            tuple: (first_arg_id, processed_args_string)
        """
        # Extract ID of the first argument if it's a Call
        first_arg_id = None
        if args and isinstance(args[0], Call):
            try:
                if isinstance(args[0].func, Attribute):
                    first_arg_id = args[0].func.value.id
                else:
                    first_arg_id = args[0].func.id
            except AttributeError:
                # Handle case when ID cannot be extracted
                first_arg_id = None

        # Determine formatting based on context
        is_jsx_context = (self.inside_return or self.direct_parent[1] == 'render')
        is_react_component = self.is_react_component(function_name)

        if is_jsx_context and is_react_component:
            # JSX mode - no separators between children
            separator = ""
            wrap_string = True
        else:
            # Normal function call mode - comma-separated args
            separator = ", "
            wrap_string = False

        # Special case: React Fragment shorthand
        if function_name == 'Fragment':
            processed_args = [self.process_arg(arg, wrap_string=wrap_string) for arg in args]
            return first_arg_id, f"<>{''.join(processed_args)}</>"

        # Process arguments based on first argument type
        if first_arg_id == 'dict':
            # Skip the first argument (dict) when processing
            args_to_process = args[1:]
        else:
            # Process all arguments
            args_to_process = args

        # Generate the processed arguments string
        processed_args = [self.process_arg(arg, wrap_string=wrap_string) for arg in args_to_process]
        args_string = separator.join(processed_args)

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

