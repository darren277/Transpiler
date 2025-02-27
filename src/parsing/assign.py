""""""
import ast
from ast import *

N = '\n'

augment_op_dict = {
    ast.Add: lambda e: '+',
    ast.Sub: lambda e: '-',
    ast.Mult: lambda e: '*',
    ast.Div: lambda e: '/',
    ast.Mod: lambda e: '%',
    ast.Pow: lambda e: '**',
    ast.FloorDiv: lambda e: '//',
    ast.BitAnd: lambda e: '&',
    ast.BitOr: lambda e: '|',
    ast.BitXor: lambda e: '^',
    ast.LShift: lambda e: '<<',
    ast.RShift: lambda e: '>>'
}

class AssignVisitor:
    # TODO: Handle reassignment to already declared consts/vars... #
    ## Note that this may involve some kind of DIY stack trace implementation to keep track of local variables... ##
    # TODO: Proper handling of semicolons at the end of statements... #

    ## TODO: Also, multiple assignments in same statement...
    def _process_assign(self, e, augment=False) -> str:
        """
        Process assignment statements, handling various assignment types and augmented assignments.

        Args:
            e: The assignment expression node
            augment: Whether this is an augmented assignment (+=, -=, etc.)

        Returns:
            str: Processed assignment statement as a string
        """
        # Handle augmented assignments (+=, -=, etc.)
        if augment:
            return self._process_augmented_assignment(e)

        # Process assignment targets
        targets = ", ".join([self.process_target(t) for t in e.targets])

        # Determine if value is a constructor needing 'new'
        new_prefix = self._determine_new_prefix(e.value)

        # Process the value based on its type
        assignment_type, value = self._process_assignment_value(e.value)

        # Construct the final assignment statement
        return self._build_assignment_statement(targets, assignment_type, augment, new_prefix, value)

    def _process_augmented_assignment(self, e) -> str:
        """
        Process augmented assignments like +=, -=, etc.

        Args:
            e: The augmented assignment expression node

        Returns:
            str: Processed augmented assignment statement
        """
        # Handle floor division special case
        if isinstance(e.op, ast.FloorDiv):
            # Remember that `//` is singe line comment notation in JavaScript, so we'll have to process this expression into a regular floor division (Math.floor()).
            # This *could* potentially lead to some very strange, albeit very rare, edge cases.
            return f"{self.process_statement(e.target)} = Math.floor({self.process_statement(e.target)} / {self.process_statement(e.value)})"

        # Get the augmentation operator string
        augment_op = augment_op_dict.get(type(e.op), lambda op: self.throw(f"NOT YET IMPLEMENTED: {type(op)}"))(e.op)

        # Process the target and value
        target = self.process_statement(e.target)
        value = self.process_statement(e.value)

        # No declaration keyword needed for augmented assignments
        return f"{target} {augment_op}= {value}"

    def _determine_new_prefix(self, value_node) -> str:
        """
        Determine if 'new' keyword is needed for constructors.

        Args:
            value_node: The value expression node

        Returns:
            str: 'new ' or empty string
        """
        if not isinstance(value_node, ast.Call):
            return ''

        # Don't use 'new' for special functions or already defined functions
        special_functions = {'ternary', 'var', 'const', 'let', 'dict'}

        try:
            func_id = value_node.func.id
            if func_id in special_functions:
                return ''
            if self.is_already_defined(func_id):
                return ''
            return 'new '
        except AttributeError:
            return ''

    def _process_assignment_value(self, value_node) -> tuple:
        """
        Process the value part of an assignment based on its type.

        Args:
            value_node: The value expression node

        Returns:
            tuple: (assignment_type, processed_value)
        """
        # Handle Call nodes (function calls)
        if isinstance(value_node, ast.Call):
            try:
                func_id = value_node.func.id

                # Handle declaration keywords (var, const, let)
                if func_id in {'var', 'const', 'let'}:
                    return func_id, value_node.args[0].value

                # Handle dictionary creation
                elif func_id == 'dict':
                    kwargs = value_node.keywords
                    if kwargs:
                        keys, values = zip(*[(keyword.arg, keyword.value) for keyword in kwargs])
                        actual_dict = ast.Dict(keys=keys, values=values)
                        return self.config.assign, self.process_dict(actual_dict)
                    else:
                        return self.config.assign, '{}'

                # Handle all other function calls
                else:
                    return self.config.assign, self.process_statement(value_node)

            except AttributeError:
                # Handle case where func doesn't have id (e.g., it's an attribute)
                return self.config.assign, self.process_statement(value_node)

        # Handle ternary expressions
        elif isinstance(value_node, ast.IfExp):
            ternary_value = self.process_ternary(
                value_node.test,
                value_node.body,
                value_node.orelse
            )
            return self.config.assign, ternary_value

        # Handle all other value types
        else:
            return self.config.assign, self.process_statement(value_node)

    def _build_assignment_statement(self, targets, assignment_type, augment, new_prefix, value) -> str:
        """
        Build the final assignment statement string.

        Args:
            targets: Processed target(s) string
            assignment_type: Type of assignment (var, const, let, etc.)
            augment: Whether this is an augmented assignment
            new_prefix: 'new ' prefix if needed
            value: Processed value string

        Returns:
            str: Complete assignment statement
        """
        # Special cases where declaration keyword should be omitted
        if 'this' in targets or augment or targets.strip() in self.config.assign_special_cases:
            return f"{targets} = {new_prefix}{value}"
        else:
            return f"{assignment_type} {targets} = {new_prefix}{value}"