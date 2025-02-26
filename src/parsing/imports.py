""""""

import ast
from ast import Import, ImportFrom, Expr, alias


class ImportVisitor:
    def __init__(self):
        self.imported_components = []
        self.import_lines = []

    def parse_import(self, line: str) -> str:
        """Parse Python import statement and convert to JavaScript import statement."""
        # Parse the line into an AST node
        node = ast.parse(line).body[0]

        # Handle different types of imports
        if isinstance(node, Import):
            result = self._handle_standard_import(node)
        elif isinstance(node, ImportFrom):
            result = self._handle_from_import(node)
        elif isinstance(node, Expr) and hasattr(node.value, 'func') and hasattr(node.value.func, 'id') and node.value.func.id == 'import_':
            result = self._handle_special_import(node)
        else:
            raise ValueError(f"Unsupported import type: {type(node)}")

        self.import_lines.append(result)
        return result

    def _handle_standard_import(self, node: Import) -> str:
        """Handle standard Python import: import os"""
        alias_strs = []
        for alias_node in node.names:
            self.imported_components.append(alias_node.name)
            if alias_node.asname:
                alias_strs.append(f'{alias_node.name} as "{alias_node.asname}"')
            else:
                alias_strs.append(f'"{alias_node.name}"')

        return f"import {', '.join(alias_strs)}"

    def _handle_from_import(self, node: ImportFrom) -> str:
        """Handle Python from-import: from module import name1, name2"""
        module_name = node.module.replace('_', '-')

        # Handle star import: from settings import *
        if len(node.names) == 1 and node.names[0].name == '*':
            self.imported_components.append(module_name)
            return f"import * as {module_name} from \"{module_name}\""

        # Handle regular import: from module import name1, name2
        imports = []
        for alias_node in node.names:
            self.imported_components.append(alias_node.name)
            if alias_node.asname:
                imports.append(f"{alias_node.name} as {alias_node.asname}")
            else:
                imports.append(alias_node.name)

        return f"import {{ {', '.join(imports)} }} from \"{module_name}\""

    def _handle_special_import(self, node: Expr) -> str:
        """Handle special import_() function."""
        args = node.value.args
        kwargs = {kw.arg: kw.value for kw in node.value.keywords}

        # Get _from kwarg value
        from_value = kwargs.get('_from')
        from_str = f"'{from_value.value}'" if from_value else None

        # Handle import with _as keyword
        if '_as' in kwargs and from_value:
            as_value = kwargs['_as'].value
            self.imported_components.append(as_value)
            return f"import * as {as_value} from {from_str}"

        # Handle multiple args with from
        if len(args) > 1 and from_value:
            imports = []
            for arg in args:
                if ' as ' in arg.value:
                    name, alias = arg.value.split(' as ')
                    imports.append(f"{name} as {alias}")
                    self.imported_components.append(alias)
                else:
                    imports.append(arg.value)
                    self.imported_components.append(arg.value)
            return f"import {{ {', '.join(imports)} }} from {from_str}"

        # Handle single arg with from
        if args and from_value:
            arg_value = args[0].value
            # Check if the arg already has curly braces
            if arg_value.startswith('{ ') and arg_value.endswith(' }'):
                self.imported_components.append(arg_value[2:-2])
                return f"import {arg_value} from {from_str}"
            else:
                self.imported_components.append(arg_value)
                return f"import {arg_value} from {from_str}"

        # Handle import without from
        if args:
            return f"import '{args[0].value}'"

        raise ValueError("Invalid import_ format")

    def add_other_imports(self) -> str:
        """Join all import lines with newlines."""
        return '\n'.join(self.import_lines)


