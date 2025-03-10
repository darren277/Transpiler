""""""
import ast
from _ast import *

from src.parsing.assign import AssignVisitor
from src.parsing.imports import ImportVisitor
from src.parsing.iterables import IterablesVisitor
from src.parsing.named_call import NamedCallVisitor
from src.react import HTML_TAGS
from src.typedefs import StatementType, BodyType, ClsType, TargetType, ArgType
from utils import pre_hook_wrapper, post_hook_wrapper, compare_ops, return_func, NOT, OR, AND, operators, N
from jsbeautifier import beautify

class Visitor(NamedCallVisitor, IterablesVisitor, AssignVisitor):
    def parse_import(self, line):
        visitor = ImportVisitor()
        result = visitor.parse_import(line)
        self.imported_components.extend(visitor.imported_components)
        self.import_lines.append(result)
        return result

    def transpile(self, linting_options: dict = None) -> str:
        s = self.process_body(self.ast.body)
        opts = dict()
        if linting_options:
            opts.update(linting_options)
        if self.config.react_app:
            opts.update(e4x=True)
            s = "import React from 'react';\n\n" + self.add_other_imports() + s
            if not self.default_export:
                s = s + '\n\nexport default App;\n\n'
        return beautify(s, opts=opts)

    def add_other_imports(self):
        return "\n".join(self.import_lines)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_body(self, body: BodyType, cls: bool = False, constructor: bool = False) -> str:
        s = ''
        for node in body:
            if constructor == True and self.config.react_app:
                s += 'super(props)\n'
            s += self.process_statement(node, cls=cls)
            if len(s) > 0: s += '\n'
        return s

    def process_left(self, left) -> str:
        # Kept as separate functions just in case you need to process them differently...
        return self.process_side(left)

    def process_right(self, right) -> str:
        # Kept as separate functions just in case you need to process them differently...
        return self.process_side(right)

    def process_side(self, side) -> str:
        return self.process_bin_op(side) if type(side) == BinOp else self.process_statement(side)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_compare(self, cmp: ast.Compare) -> str:
        # cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
        left = self.process_left(cmp.left)
        right = self.process_right(cmp.comparators[0])
        return f"{left} {compare_ops[type(cmp.ops[0])]} {right}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_arg(self, a: ArgType, wrap_string=False) -> str:
        case_switch = {
            arg: lambda a: self.process_funcdef_arg(a),
            Call: lambda a: self.process_call(a),
            Name: lambda a: f'{{{a.id}}}' if wrap_string else a.id,
            Attribute: lambda a: '{' + self.process_attribute(a) + '}' if wrap_string else self.process_attribute(a),

            Constant: lambda a: '{' + self.process_constant(a) + '}' if wrap_string else self.process_constant(a),

            UnaryOp: lambda a: self.process_unary_op(a),
            # BinOp: lambda a: self.process_bin_op(a),
            Compare: lambda a: self.process_compare(a),
            BoolOp: lambda a: self.process_bool_op(a),
            Lambda: lambda a: self.process_lambda(a),

            JoinedStr: lambda a: '{' + self.process_joined_string(a) + '}' if wrap_string else self.process_joined_string(a),

            Tuple: lambda a: self.process_tuple(a),
            List: lambda a: self.process_list(a),
            Dict: lambda a: self.process_dict(a),
            Set: lambda a: self.process_set(a),

            Subscript: lambda a: self.process_subscript(a),

            Starred: lambda a: f"**{a.value.id}",

            ListComp: lambda a: '{' + self.process_list_comp(a) + '}' if wrap_string else self.process_list_comp(a),
        }
        if type(a) == BinOp:
            if type(a.op) == Mult: return self.process_bin_op(a)
            # These do the same thing. Not sure why I added the Mult case specifically.
            # Leaving it in for now in case it was for some anticipated edge case.
            return self.process_bin_op(a)
        else:
            return case_switch.get(type(a), lambda a: self.throw(f"NOT YET IMPLEMENTED: {type(a)}"))(a)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_bool_op(self, arg: ast.BoolOp or ast.Constant) -> str:
        if type(arg) == ast.Constant:
            return self.process_arg(arg)
        if type(arg.op) == Or:
            return f' {self.config.OR} '.join([self.process_statement(val) for val in arg.values])
        elif type(arg.op) == And:
            return f' {self.config.AND} '.join([self.process_statement(val) for val in arg.values])
        elif type(arg.op) == Not:
            # Is there a possible case where this would be an array longer than 1?
            return f"{self.config.NOT}{self.process_statement(arg.values[0])}"
        # Does this ever really happen? breakpoint(); raise Exception("BoolOp and ternary...")

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_attribute(self, body: ast.Attribute, s: str = "") -> str:
        if type(body.value) == Call:
            return self.process_attribute_call(body.value)
        last_attr = body.attr
        if type(body.value) == Name:
            #if self.config.debug: print(f"{body.value} IS A NAME... NO RECURSION...")
            v = body.value.id
            s = self.config._self + s if v == 'self' else v + s
        else:
            s = self.process_statement(body.value) + s
        s += "." + last_attr
        return s

    def process_chained_call(self, call, s: str = "") -> str:
        return self.process_attribute_call(call, s=s)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_attribute_call(self, call: ast.Call, s: str = "") -> str:
        # TODO: This is messy.
        if hasattr(call, 'func') and hasattr(call.func, 'value') and hasattr(call.func.value, 'id') and call.func.value.id == 'self':
            call.func.value.id = 'this'

        # Ensure we have a valid call
        if not hasattr(call, 'func'):
            raise Exception("Invalid call object - missing func attribute")

        # Process the function part of the call
        if isinstance(call.func, ast.Attribute):
            # Get the base value first (e.g., UserService.getUsers())
            value_str = ""

            if isinstance(call.func.value, ast.Call):
                # Handle nested calls (e.g., getUsers().then())
                value_str = self.process_attribute_call(call.func.value)
            elif isinstance(call.func.value, ast.Name):
                value_str = call.func.value.id
            elif isinstance(call.func.value, ast.JoinedStr):
                value_str = self.process_joined_string(call.func.value)
            elif isinstance(call.func.value, ast.Attribute):
                value_str = self.process_attribute(call.func.value)
            elif isinstance(call.func.value, ast.Subscript):
                value_str = self.process_subscript(call.func.value)
            elif isinstance(call.func.value, ast.List):
                value_str = self.process_list(call.func.value)

            # Process the actual call with its arguments
            call_str = self.process_named_call(call)

            # Combine the parts
            if value_str:
                # If we have a value, add the method call with a dot
                return f"{value_str}.{call_str}"
            else:
                # If no value (shouldn't happen), just return the call
                return call_str

        elif isinstance(call.func, ast.Call):
            # Direct function calls
            return self.process_named_call(call)
        elif isinstance(call.func, ast.Name):
            # Simple named function calls
            return self.process_named_call(call)
        else:
            raise Exception(f"Unexpected function type in call: {type(call.func)}")

    def is_already_defined(self, function_name: str) -> bool:
        return (function_name in self.imported_components) or (function_name in self.defined_classes) or (function_name in self.defined_functions)

    def is_react_component(self, function_name: str):
        if function_name in self.event_handlers: return False
        return (((function_name.lower() == 'Fragment'.lower()) or (function_name.lower() in HTML_TAGS) or self.is_already_defined(function_name)))

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_named_call(self, call: ast.Call) -> str:
        return self._process_named_call(call)

    def process_val(self, value, style: bool = False):
        return self._process_val(value, style=style)

    def process_dict_key(self, key) -> str:
        return self._process_dict_key(key)

    def process_dict(self, d) -> str:
        return self._process_dict(d)

    def process_set(self, s) -> str:
        return self._process_set(s)

    def process_list(self, l) -> str:
        return self._process_list(l)

    def process_tuple(self, t) -> str:
        return self._process_tuple(t)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_target(self, t: TargetType) -> str:
        case_switch = {
            Name: lambda t: self.process_name(t),
            Attribute: lambda t: self.process_attribute(t),
            Tuple: lambda t: self.process_tuple(t),
            List: lambda t: self.process_list(t)
        }
        return case_switch.get(type(t), lambda t: self.throw(f"NOT YET IMPLEMENTED: {type(t)}"))(t)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_for_loop(self, f: ast.For) -> str:
        # TODO: orelse = self.process_statement(f.orelse)
        orelse = ''

        _iter = f.iter

        if type(_iter) == Constant or (type(_iter) == Call and _iter.func.id == 'range'):
            t = self.process_target(f.target)
            if type(_iter) == Constant or len(_iter.args) == 1:
                if type(_iter) == Constant: arg1 = _iter
                else: arg1 = _iter.args[0]
                return f"for (let {t} = 0; {t} < {self.process_arg(arg1)}; {t}++) {{{self.process_body(f.body)}}} {orelse}"
            elif len(_iter.args) == 2:
                arg1, arg2 = _iter.args
                return f"for (let {t} = {self.process_arg(arg2)}; {t} < {self.process_arg(arg1)}; {t}++) {{{self.process_body(f.body)}}} {orelse}"
            elif len(_iter.args) == 3:
                arg1, arg2, arg3 = _iter.args
                arg3 = self.process_arg(arg3)
                direction = '+' if int(arg3) >= 0 else '-'
                return f"for (let {t} = {self.process_arg(arg2)}; {t} {'<' if direction == '+' else '>'} {self.process_arg(arg1)}; {t}{direction}={arg3}) {{{self.process_body(f.body)}}} {orelse}"
        else:
            raise Exception("NOT YET IMPLEMENTED")

    @return_func
    def process_return(self, r) -> str:
        if not self.config.wrap_return or len(self.config.wrap_return) == 0:
            wrap_return_left = ''
            wrap_return_right = ''
        else:
            wrap_return_left = self.config.wrap_return[0]
            wrap_return_right = self.config.wrap_return[1]
        ## NOTE: LOTS OF SPECIAL CASES FOR REACT... ##
        #if self.config.debug: print("RETURN", type(r), r)
        expr = r.value
        if type(expr) == Tuple:
            tuple_body = ", ".join([self.process_statement(el) for el in expr.elts])
            raise Exception(f"TODO: Return of ({tuple_body})")
        if expr == None:
            if self.config.debug: print("Function returns nothing.")
            expr = ""
        else:
            expr = self.process_statement(expr)
        return f"return {wrap_return_left}{expr}{wrap_return_right}{self.config.end_statement}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_assign(self, e, augment=False) -> str:
        return self._process_assign(e, augment=augment)

    def process_subscript(self, e) -> str:
        try:
            return f"{e.value.id}[{e.slice.id}]"
        except:
            return f"{self.process_statement(e.value)}[{self.process_statement(e.slice)}]"
            # This can't happen can it? except: raise Exception("NOT YET IMPLEMENTED FOR SUBSCRIPT...")

    def process_name(self, e) -> str:
        return e.id

    def check_call(self, c) -> str:
        return f"{c}" if self.direct_parent[0] in ['JoinedStr', 'lambda'] else c

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_statement(self, statement: StatementType, cls: bool = False) -> str:
        e = statement
        e_type = type(e)
        case_switch = {
            Assign: lambda e: self.process_assign(e) + '\n',
            AsyncFunctionDef: lambda e: self.process_function(e, cls=cls, _async=True),
            FunctionDef: lambda e: self.process_function(e, cls=cls),
            Expr: lambda e: self.process_statement(e.value),
            Call: lambda e: self.check_call(self.process_call(e)),
            Return: lambda e: self.process_return(e), # noqa
            Name: lambda e: self.process_name(e),
            Attribute: lambda e: self.process_attribute(e),
            Constant: lambda e: self.process_constant(e),
            If: lambda e: self.process_if(e),
            IfExp: lambda e: self.process_if(e),
            UnaryOp: lambda e: self.process_unary_op(e),
            BinOp: lambda e: self.process_bin_op(e),
            Compare: lambda e: self.process_compare(e),
            BoolOp: lambda e: self.process_bool_op(e),
            Lambda: lambda e: self.process_lambda(e),
            JoinedStr: lambda e: self.process_joined_string(e),
            Subscript: lambda e: self.process_subscript(e),
            ClassDef: lambda e: self.process_cls(e),
            While: lambda e: self.process_while(e),
            AugAssign: lambda e: self.process_assign(e, augment=True),
            Tuple: lambda e: self.process_tuple(e),

            Dict: lambda e: self.process_dict(e),
            List: lambda e: self.process_list(e),
            Set: lambda e: self.process_set(e),

            For: lambda e: self.process_for_loop(e),

            Try: lambda e: self.process_try(e),
            ExceptHandler: lambda e: self.process_except(e),

            ListComp: lambda e: self.process_list_comp(e),
            DictComp: lambda e: self.process_dict_comp(e),
            SetComp: lambda e: self.process_set_comp(e),

            Assert: lambda e: self.process_assert(e),

            Starred: lambda e: f"...{e.value.id}",

            Pass: lambda e: ''
        }
        s = case_switch.get(e_type, lambda e: self.throw(f"NOT YET IMPLEMENTED: {e_type}"))(e)
        end_statement = ""
        if len(s) == 0:
            return ""
        return f"{s}{end_statement}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_assert(self, a: ast.Assert) -> str:
        return f"console.assert({self.process_arg(a.test)}, '{self.process_arg(a.test)}')"

    def process_list_comp(self, e) -> str:
        return self._process_list_comp(e)

    def process_dict_comp(self, e) -> str:
        return self._process_dict_comp(e)

    def process_set_comp(self, e) -> str:
        return self._process_set_comp(e)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_try(self, t: ast.Try) -> str:
        try_block = self.process_body(t.body)
        except_block = self.process_body(t.handlers)
        finally_string = ""
        if t.orelse:
            else_block = self.process_body(t.orelse)
            raise Exception("TODO: Implement else block for try/except")
        if t.finalbody:
            finally_block = self.process_body(t.finalbody)
            finally_string = f"\nfinally {{{N+finally_block}}}"
        return f"try {{{try_block}}}\ncatch (e) {{{except_block}}}" + finally_string

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_except(self, e: ast.ExceptHandler) -> str:
        # logger.warn...
        if e.type:
            print(f"WARNING: In JS you need to handle specific error types (i.e. {e.type.id}) internally inside the `catch` block.")
        return self.process_body(e.body)

    # TODO: STILL NEEDS TYPING...
    @pre_hook_wrapper
    @post_hook_wrapper
    def process_while(self, e) -> str:
        test = self.process_compare(e.test) if type(e.test) == Compare else self.process_arg(e.test)
        return f"while ({test}) {{{N.join([self.process_statement(s) for s in e.body])}}}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_call(self, c: ast.Call) -> str:
        assert type(c) == Call
        if type(c) == JoinedStr: breakpoint()
        if type(c.func) == Call:
            return self.process_chained_call(c)
        return self.process_attribute_call(c) if type(c.func) == Attribute else self.process_named_call(c)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_constant(self, e: ast.Constant) -> str:
        case_switch = {
            int: lambda val: f"{val}",
            str: lambda val: f"\"{val}\"",
            type(...): lambda val: self.config._ellipsis,
            type(None): lambda val: self.config.none,
            float: lambda val: f"{val}",
            bool: lambda val: str(val).lower()
        }
        val = e.value
        return case_switch.get(type(val), lambda val: self.throw(f"NOT YET IMPLEMENTED: {type(val)}"))(val)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_unary_op(self, e: ast.UnaryOp) -> str:
        # unaryop = Invert | Not | UAdd | USub
        case_switch_dict = {
            USub: lambda e: f"-{self.process_statement(e.operand)}",
            Not: lambda e: f"!{self.process_statement(e.operand)}",
            UAdd: lambda e: f"+{self.process_statement(e.operand)}",
            Invert: lambda e: f"~{self.process_statement(e.operand)}"
        }
        return case_switch_dict.get(type(e.op), lambda e: self.throw(f"NOT YET IMPLEMENTED: {type(e.op)}"))(e)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_if(self, e: ast.If) -> str:
        yo = N.join([self.process_statement(exp) for exp in e.body]) if type(e.body) == list else self.process_statement(e.body)
        self.direct_parent = ('conditional', None)

        orelse = ""

        if e.orelse:
            orelse = f"else {{\n{self.process_statement(e.orelse)}\n}}"

        if type(e.test) == Name:
            return f"if ({e.test.id}) {{{N + yo + N}}} {orelse}"
        else:
            return f"if ({self.process_compare(e.test) if type(e.test) == Compare else self.process_bool_op(e.test)}) {{{N + yo + N}}} {orelse}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_bin_op(self, body: ast.BinOp, double_and: bool = False, special_long_lambda_case: bool = False) -> str:
        # operator = Add | Sub | Mult | MatMult | Div | Mod | Pow
        # LShift | RShift
        # BitOr | BitXor | BitAnd | FloorDiv
        if double_and:
            op = '&&'
        else:
            op = operators[type(body.op)]
        left = f"({self.process_left(body.left)})" if type(body.left) == BinOp else self.process_left(body.left)
        right = f"({self.process_right(body.right)})" if type(body.right) == BinOp else self.process_left(body.right)
        if special_long_lambda_case and (op != '+') and (op != '-') and (op != '*') and (op != '/') and (op != '//'):
            # What exactly is this case about?
            op = ''
            return f"{left} {op} {right}"
        else:
            if op == '//':
                return f"Math.floor({left} / {right})"
            return f"{left} {op} {right}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_lambda(self, l: ast.Lambda, is_event_handler: bool = False) -> str:
        """
        Process a lambda expression, with special handling for event handlers.

        Args:
            l: The lambda AST node
            is_event_handler: Boolean indicating if this lambda is an event handler
        """
        args, body = l.args, l.body
        args_string = ', '.join([str(arg.arg) for arg in args.args]) if args.args else ''
        self.direct_parent = ('lambda', None)

        # Process the body
        if isinstance(body, ast.BinOp):
            # Special case for longer lambdas in Python
            body_string = self.process_bin_op(body, special_long_lambda_case=True)
        elif is_event_handler and isinstance(body, ast.Call):
            # Special case for event handler lambdas with simple function calls
            func_name = body.func.id if isinstance(body.func, ast.Name) else self.process_statement(body.func)
            args_list = [self.process_statement(arg) for arg in body.args]
            body_string = f"{func_name}({', '.join(args_list)})"
        else:
            body_string = self.process_statement(body)

        # Format the body based on complexity and type
        if is_event_handler and isinstance(body, ast.Call):
            # Simple event handler - no extra wrapping needed
            body_wrapper = body_string
        elif self.is_complex_body(body) and self.config.wrap_return:
            # Complex body - use curly braces and return
            body_wrapper = f"{{ return {self.config.wrap_return[0]}{body_string}{self.config.wrap_return[1]} }}"
        elif isinstance(body, ast.Dict):
            # Special case for lambdas that return a dictionary
            body_wrapper = f"{{ return {body_string} }}"
        else:
            # Simple body - no curly braces needed
            body_wrapper = body_string

        # Format the complete lambda
        if len(args.args) == 1:
            return f"{args_string} => {body_wrapper}"
        else:
            return f"({args_string}) => {body_wrapper}"

    def is_complex_body(self, body: ast.AST) -> bool:
        """
        Determine if a lambda body is complex enough to need curly braces and return.

        Args:
            body: The AST node representing the lambda body
        """
        # Add cases as needed for your specific requirements
        return (
                isinstance(body, (ast.BinOp, ast.IfExp)) or
                (isinstance(body, ast.Call) and hasattr(body, 'keywords') and body.keywords) or
                hasattr(body, 'body')  # Check for compound statements
        )

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_joined_string(self, body: ast.JoinedStr) -> str:
        original_direct_parent = self.direct_parent[0], self.direct_parent[1]
        self.direct_parent = ('JoinedStr', None)
        s = "".join([val.value if type(val) == Constant else f"${{{val.id}}}" if type(val) == Name else f"${{{self.process_statement(val.value)}}}" for val in body.values])
        self.direct_parent = original_direct_parent
        return f"`{s}`"

    # TODO: STILL NEEDS TYPING...
    @pre_hook_wrapper
    @post_hook_wrapper
    def process_ternary(self, *args) -> str:
        if len(args) != 3:
            raise Exception("Ternary operator must have 3 arguments.")
        else:
            self.inside_custom_ternary = True
            arg1, arg2, arg3 = [self.process_arg(arg) for arg in args]
            self.inside_custom_ternary = False
            return f"{arg1} ? {arg2} : {arg3}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_function(self, func: ast.FunctionDef, cls: bool = False, _async: bool = False) -> str:
        self.defined_functions.append(func.name)

        n_defaults = len(_defaults := func.args.defaults)
        _defaults = iter(_defaults)
        args = [arg for arg in func.args.args if arg.arg != 'self']
        n_args = len(args)
        defaults = [next(_defaults) if i >= n_args-n_defaults else None for i in range(n_args)]
        arg_string = ', '.join([self.process_funcdef_arg(arg, default) for arg, default in zip(args, defaults)])
        returns = ' -> ' + self.process_statement(func.returns) if func.returns else ''
        ## TODO: decorators = "\n".join([f"@{self.process_statement(decorator)}" for decorator in func.decorator_list]) if func.decorator_list else ""

        func_name = 'constructor' if func.name == '__init__' else func.name
        if func_name == 'constructor' and 'props' not in arg_string and self.config.react_app:
            arg_string = 'props'

        func_prefix = '' if cls or self.direct_parent[0] == 'cls' else 'function '
        self.direct_parent = ('func', func_name)
        body = self.process_body(func.body, constructor=True if func_name == 'constructor' else False)

        if _async:
            func_prefix = 'async ' + func_prefix

        decorator_list = func.decorator_list
        if decorator_list:
            if decorator_list[0].id == 'staticmethod':
                func_prefix = 'static ' + func_prefix
            else:
                raise Exception('new kind of decorator...')

        return f"{func_prefix}{func_name} ({arg_string}){returns} {{ {body} }}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_funcdef_arg(self, a: ast.arg, default = None) -> str:
        if self.config.react_app and a.arg == 'props':
            # Maybe not ideal, but doing this for now until I come up with a better solution...
            return '{props}'

        hint = ': ' + self.process_statement(a.annotation) if a.annotation else ''
        default = ' = ' + self.process_statement(default) if default else ''
        return f"{a.arg}{hint}{default}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_cls(self, cls: ClsType) -> str:
        self.defined_classes.append(cls.name)
        # Note that JavaScript cannot handle multiple inheritence in a straightforward manner.
        # You would have to create a mixin (a separate class), which is a bit out of the scope of this project.
        inherits = ''
        if cls.bases:
            if len(cls.bases) > 1:
                raise Exception("JS does not handle multiple inheritence like this. You must define a mixin yourself.")
            inherits += ' extends '
            try:
                inherits += cls.bases[0].id
            except AttributeError:
                # cls.bases[0] is likely an ast.Attribute...
                inherits += self.process_attribute(cls.bases[0])
        self.direct_parent = ('cls', cls.name)
        body = self.process_body(cls.body, cls=True)
        return f"class {cls.name}{inherits} {{{body}}}"

    def register_event_handler(self, handler: str):
        self.event_handlers.append(handler)
