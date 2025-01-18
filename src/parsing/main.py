""""""
import ast
from _ast import *

from src.react import HTML_TAGS
from src.typedefs import StatementType, BodyType, ClsType, TargetType, ArgType
from utils import pre_hook_wrapper, post_hook_wrapper, compare_ops, return_func, NOT, OR, AND, operators, N
from jsbeautifier import beautify

class Visitor:
    def parse_import(self, line: str):
        # TODO: Why not actually parse these lines with the actual ast parser library, lol?
        # You use it for literally everything else.
        if line.startswith('from'):
            # from special_types import var, const, let, ternary
            actual_line = line.replace('from ', '').split(' import ')
            source = actual_line[0].replace('src.react', 'react')
            components = actual_line[1]
        else:
            line = line.replace('._import._from', '')
            components, source = line.split(' = ')

        separated_components = components.split(', ')
        source = source.replace('.', '/')
        source = f'"{source}"'

        for component in separated_components:
            self.imported_components.append(component)

        self.import_lines.append(f"import {{{components}}} from {source};")

    def transpile(self, linting_options: dict = None) -> str:
        s = self.process_body(self.ast.body)
        opts = dict()
        if linting_options:
            opts.update(linting_options)
        if self.config.react_app:
            opts.update(e4x=True)
            s = "import React from 'react';\n\n" + self.add_other_imports() + s
            s = s + '\n\nexport default App;\n\n'
        return beautify(s, opts=opts)

    def add_other_imports(self):
        return "\n".join(self.import_lines)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_body(self, body: BodyType, cls: bool = False, constructor: bool = False) -> str:
        s = ''
        for node in body:
            if constructor == True:
                s += 'super(props)\n'
            s += self.process_statement(node, cls=cls)
            #if len(s) > 0: s += '\n'
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
            Attribute: lambda a: self.process_attribute(a),

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

            Starred: lambda a: f"**{a.value.id}"
        }
        if type(a) == BinOp:
            if type(a.op) == Mult:
                return self.process_bin_op(a)
            return self.process_bin_op(a)
        else:
            return case_switch.get(type(a), lambda a: self.throw(f"NOT YET IMPLEMENTED: {type(a)}"))(a)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_bool_op(self, arg: ast.BoolOp) -> str:
        if type(arg) == ast.Constant:
            return self.process_arg(arg)
        if type(arg.op) == Or:
            return f"{self.process_statement(arg.values[0])} {OR} {self.process_statement(arg.values[1])}"
        elif type(arg.op) == And:
            return f"{self.process_statement(arg.values[0])} {AND} {self.process_statement(arg.values[1])}"
        elif type(arg.op) == Not:
            return f"{NOT} {self.process_statement(arg.operand)}"
        else:
            breakpoint()
            raise Exception("BoolOp and ternary...")

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
            #if self.config.debug: print("NOW RECURSING...")
            s = self.process_attribute(body.value, s) + s
        s += "." + last_attr
        return s

    def process_chained_call(self, call, s: str = "") -> str:
        return self.process_attribute_call(call, s=s)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_attribute_call(self, call: ast.Call, s: str = "") -> str:
        if call.func.value.id == 'self':
            call.func.value.id = 'this'
        try:
            call_func = call.func
        except:
            raise Exception("You're passing something in that is not an actual call... check your if else chain directly below...")
        if type(call.func) == Attribute:
            if type(call.func.value) == Name:
                s = call.func.value.id + s
            elif type(call.func.value) == JoinedStr:
                s = self.process_joined_string(call.func.value) + s
            elif type(call.func.value) == Attribute:
                s = self.process_attribute(call.func.value) + s
            elif type(call.func.value) == Subscript:
                s = self.process_subscript(call.func.value) + s
            elif type(call.func.value) == List:
                print("Yes, you can chain functions to lists in JS.")
                s = self.process_list(call.func.value) + s
            else:
                ## NOTE: You should not be passing an attribute to the following function...
                ## if type(call.func.value) == Attribute: breakpoint()
                s = self.process_attribute_call(call.func.value, s) + s
        elif type(call.func) == Call:
            raise Exception("Hmmm....")
        last_call = self.process_named_call(call)
        s += last_call if (type(call.func) == Name) or (type(call.func) == Call) else "." + last_call
        if s.startswith('.'):
            breakpoint()
        return s

    def is_already_defined(self, function_name: str) -> bool:
        return (function_name in self.imported_components) or (function_name in self.defined_classes) or (function_name in self.defined_functions)

    def is_react_component(self, function_name: str):
        return (((function_name.lower == 'Fragment'.lower()) or (function_name.lower() in HTML_TAGS) or self.is_already_defined(function_name)))

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_named_call(self, call: ast.Call) -> str:
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
            close1, close2 = ('/', '') if function_name.lower() in self.imported_components else ('', f'</{function_name}>')
            if content:
                actual_contents = [kw.value for kw in kwargs if kw.arg == 'content'][0]
                kwargs_string += ", ".join([f"{kw.arg}={self.process_arg(kw.value)}" for kw in kwargs if not kw.arg == 'content'])
                return f"<{function_name}{kwargs_string.replace(', ', ' ')}{close1}>{self.process_statement(actual_contents)}{close2}"
            else:
                kwargs_string += ", ".join([f"{kw.arg}={{{self.process_arg(kw.value)}}}" for kw in kwargs])
                if "True" in kwargs_string:
                    kwargs_string = kwargs_string.replace('="True"', '')
                return f"<{function_name}{kwargs_string.replace(', ', ' ')}{close1}>{args_string}{close2}"
        else:
            return f"{function_name}({args_string}{kwargs_string})"

    def process_dict_key(self, key) -> str:
        if type(key) == Constant:
            return self.process_constant(key)
        elif hasattr(key, 'id'):
            return key.id
        elif type(key) == str:
            # NOTE: You have the option to wrap this in double quotes or even single quotes if desired.
            # TODO: Consider if wrapping in double quotes should be the default unless otherwise specified?
            return key
        else:
            breakpoint()

    def process_dict(self, d) -> str:
        dict_body = self.config.dict_sep.join([f"{self.process_dict_key(key)}: {self.process_arg(val)}" for key, val in zip(d.keys, d.values)])
        return f"{self.config.dict_wrapper[0]} {dict_body} {self.config.dict_wrapper[1]}"

    def process_set(self, s) -> str:
        result = self.config.set_sep.join([self.process_arg(el) for el in s.elts])
        if self.config.set_wrapper and not self.config.react_app:
            return f"new Set({self.config.set_wrapper[0]}{result}{self.config.set_wrapper[1]})"
        elif self.config.react_app:
            return f"{{{result}}}"
        else:
            raise Exception("process_set() case not yet implemented.")

    def process_list(self, l) -> str:
        result = self.config.list_sep.join([self.process_statement(el) for el in l.elts])
        return f"[{result}]"

    def process_tuple(self, t) -> str:
        result = ", ".join([self.process_arg(v) for v in t.elts])
        return f"{self.config.tuple_wrapper[0]}{result}{self.config.tuple_wrapper[1]}"

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

        if type(_iter) == Constant or _iter.func.id == 'range':
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
                direction = '+' if arg3 >= 0 else '-'
                return f"for (let {t} = {self.process_arg(arg2)}; {t} {'<' if direction == '+' else '>'} {self.process_arg(arg1)}; {t}{direction}={arg3}) {{{self.process_body(f.body)}}} {orelse}"
        else:
            raise Exception("NOT YET IMPLEMENTED")

    @return_func
    def process_return(self, r) -> str:
        if not self.config.wrap_return:
            wrap_return_left = ''
            wrap_return_right = ''
        else:
            wrap_return_left = self.config.wrap_return[0]
            wrap_return_right = self.config.wrap_return[1]
        ## NOTE: LOTS OF SPECIAL CASES FOR REACT... ##
        #if self.config.debug: print("RETURN", type(r), r)
        expr = r.value
        if type(expr) == Tuple:
            raise Exception(f"TODO: Return of {str(expr)}")
        if expr == None:
            if self.config.debug: print("Function returns nothing.")
            expr = ""
        else:
            expr = self.process_statement(expr)
        return f"return {wrap_return_left}{expr}{wrap_return_right}{self.config.end_statement}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_assign(self, e, augment = False) -> str:
        augment_string = ""
        if augment:
            op_type = type(e.op)
            if op_type == ast.FloorDiv:
                # Remember that `//` is singe line comment notation in JavaScript, so we'll have to process this expression into a regular floor division (Math.floor()).
                # This *could* potentially lead to some very strange, albeit very rare, edge cases.
                return f"{e.target.id} = Math.floor({e.target.id} / {self.process_statement(e.value)})"
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
            augment_string = augment_op_dict.get(op_type, lambda e: self.throw(f"NOT YET IMPLEMENTED: {op_type}"))(e.op)
        #print("CURRENT CODE CONTEXT")
        #print(self.current_code_context)
        #if 'my_special_var' in self.current_code_context: breakpoint()
        # TODO: Handle reassignment to already declared consts/vars... #
        ## Note that this may involve some kind of DIY stack trace implementation to keep track of local variables... ##
        # TODO: Proper handling of semicolons at the end of statements... #

        ## TODO: Also, multiple assignments in same statement...
        #if self.config.debug: print("ASSIGN")
        targets = ", ".join([self.process_target(t) for t in e.targets]) if not augment else self.process_statement(e.target)
        new = 'new ' if type(e.value) == Call and not self.is_already_defined(e.value.func.id) else ''
        if type(e.value) == ast.Call:
            if e.value.func.id == 'ternary':
                new = ''
            if e.value.func.id == 'var':
                assign = 'var'
                new = ''
                val = e.value.args[0].value
            elif e.value.func.id == 'const':
                assign = 'const'
                new = ''
                val = e.value.args[0].value
            elif e.value.func.id == 'let':
                assign = 'let'
                new = ''
                val = e.value.args[0].value
            elif e.value.func.id == 'dict':
                assign = self.config.assign
                new = ''
                kwargs = e.value.keywords
                keys, values = zip(*[(keyword.arg, keyword.value) for keyword in kwargs])
                actual_dict = ast.Dict(
                    keys=keys,
                    values=values
                )
                val = self.process_dict(actual_dict)
            else:
                assign = self.config.assign
                val = self.process_statement(e.value)
        elif type(e.value) == ast.IfExp:
            assign = self.config.assign
            new = ''
            val = self.process_ternary(e.value.test, e.value.body, e.value.orelse)
        else:
            assign = self.config.assign
            val = self.process_statement(e.value)
        if 'this' in targets:
            return f"{targets} {augment_string}= {new}{val}"
        else:
            if augment or targets.strip() in self.config.assign_special_cases: return f"{targets} {augment_string}= {new}{val}"
            else: return f"{assign} {targets} {augment_string}= {new}{val}"

    def process_subscript(self, e) -> str:
        try:
            return f"{e.value.id}[{e.slice.id}]"
        except:
            try:
                return f"{self.process_statement(e.value)}[{self.process_statement(e.slice)}]"
            except:
                raise Exception("NOT YET IMPLEMENTED FOR SUBSCRIPT...")

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
            Assign: lambda e: self.process_assign(e),
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
        return f"console.assert({self.process_compare(a.test)}, '{self.process_compare(a.test)}')"

    def process_list_comp(self, e) -> str:
        if len(e.generators) > 1: raise Exception("TODO: Multiple generators in list comprehension...")
        if len(e.generators[0].ifs): raise Exception("TODO: If statements in list comprehension...")
        if e.generators[0].is_async: raise Exception("TODO: Async list comprehension...")
        return f"({self.process_statement(e.elt)} for {e.generators[0].target.id} in {self.process_statement(e.generators[0].iter)})"

    def process_dict_comp(self, e) -> str:
        if len(e.generators) > 1: raise Exception("TODO: Multiple generators in dict comprehension...")
        if len(e.generators[0].ifs): raise Exception("TODO: If statements in dict comprehension...")
        if e.generators[0].is_async: raise Exception("TODO: Async dict comprehension...")
        return f"{{ {self.process_statement(e.key)}: {self.process_statement(e.value)} for {e.generators[0].target.id} in {self.process_statement(e.generators[0].iter)} }}"

    def process_set_comp(self, e) -> str:
        if len(e.generators) > 1: raise Exception("TODO: Multiple generators in set comprehension...")
        if len(e.generators[0].ifs): raise Exception("TODO: If statements in set comprehension...")
        if e.generators[0].is_async: raise Exception("TODO: Async set comprehension...")
        return f"{{ {self.process_statement(e.elt)} for {e.generators[0].target.id} in {self.process_statement(e.generators[0].iter)} }}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_try(self, t: ast.Try) -> str:
        try_block = self.process_body(t.body)
        except_block = self.process_body(t.handlers)
        finally_string = ""
        if t.orelse:
            raise Exception("TODO: Implement else block for try/except")
            else_block = self.process_body(t.orelse)
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
        return f"while ({self.process_compare(e.test)}) {{{N.join([self.process_statement(s) for s in e.body])}}}"

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
        if type(e.test) == Name:
            return f"if ({e.test.id}) {{{N + yo + N}}}"
        else:
            return f"if ({self.process_compare(e.test) if type(e.test) == Compare else self.process_bool_op(e.test)}) {{{N + yo + N}}}"

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
            op = ''
            return f"{left} {op} {right}"
        else:
            if op == '//':
                return f"Math.floor({left} / {right})"
            return f"{left} {op} {right}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_lambda(self, l: ast.Lambda) -> str:
        args, body = l.args, l.body
        args_string = ', '.join([str(arg.arg) for arg in args.args]) if args.args else ''
        self.direct_parent = ('lambda', None)
        if type(body) == BinOp:
            ## SPECIAL CASE FOR LONGER LAMBDAS IN PYTHON ##
            body_string = self.process_bin_op(body, special_long_lambda_case=True)
        else:
            body_string = self.process_statement(body)
        return f"{args_string} => {body_string}" if len(args.args) == 1 else f"({args_string}) => {body_string}"

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
            raise Exception("TERNARY BROKE")
        else:
            self.inside_custom_ternary = True
            arg1, arg2, arg3 = [self.process_arg(arg) for arg in args]
            self.inside_custom_ternary = False
            return f"{arg1} ? {arg2} : {arg3}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_function(self, func: ast.FunctionDef, cls: bool = False) -> str:
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
        if func_name == 'constructor' and 'props' not in arg_string:
            arg_string = 'props'

        func_prefix = '' if cls or self.direct_parent[0] == 'cls' else 'function '
        self.direct_parent = ('func', func_name)
        body = self.process_body(func.body, constructor=True if func_name == 'constructor' else False)

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
