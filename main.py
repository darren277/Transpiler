""""""
import ast

from config import *
from utils import *
from parsetools import unindent
from jsbeautifier import beautify
import inspect

self_closing_tags = ['route']

class Code:
    react = True

    def __init__(self, code: str or callable, config: ASTConfig = DEFAULT_CONFIG, config_kwargs: dict = None):
        self.code = code if type(code) == str else inspect.getsource(code)
        self.imported_components = []
        self.import_lines = []

        if config_kwargs:
            config.update(config_kwargs)

        self.inside_return = False; self.inside_custom_ternary = False

        lines = self.code.splitlines()

        self.imports = [self.parse_import(line) for line in lines if '_import' in line]
        self.code = "\n".join([line for line in lines if not '_import' in line])
        self.ast = ast.parse(self.code)

        self.direct_parent = (None, None)

        # Currently placed after IF statements and ASSIGNS... #
        self.eos = ';'

        self.config = config
        self.react = self.config.react

        self.log_file = None
        self.log_file = config.log_file

    def pre_hook(self, loc):
        func_name = loc['func'].__name__
        e = loc['args'][0]
        #print("PRE HOOK", func_name, e, loc)
        #print(convert_back_to_code(self.code, e))

    def post_hook(self, loc):
        #print("POST HOOK", loc['func'].__name__, loc['args'][0], loc)
        ...

    def log(self, msg: str):
        ...

    def parse_import(self, line: str):
        line = line.replace('._import._from', '')
        components, source = line.split(' = ')
        separated_components = components.split(', ')
        source = source.replace('.', '/')
        source = f'"{source}"'

        for component in separated_components:
            self.imported_components.append(component)

        self.import_lines.append(f"import {components} from {source};")

    def transpile(self, linting_options: dict = None):
        s = self.process_body(self.ast.body)
        opts = dict()
        if linting_options:
            opts.update(linting_options)
        if self.react:
            opts.update(e4x=True)
        return beautify(s, opts=opts)

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_body(self, body, cls: bool = False):
        s = ''
        for node in body:
            s += self.process_statement(node, cls=cls)# + ";"
            if len(s) > 0:
                s += ';\n'
        return s

    def process_left(self, left):
        # Kept as separate functions just in case you need to process them differently...
        return self.process_side(left)

    def process_right(self, right):
        # Kept as separate functions just in case you need to process them differently...
        return self.process_side(right)

    def process_side(self, side):
        return self.process_bin_op(side) if type(side) == BinOp else self.process_statement(side)

    def process_compare(self, cmp):
        # cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
        left = self.process_left(cmp.left)
        right = self.process_right(cmp.comparators[0])
        return f"{left} {compare_ops[type(cmp.ops[0])]} {right}"

    def process_arg(self, a):
        case_switch = {
            arg: lambda a: self.process_funcdef_arg(a),
            Call: lambda a: self.process_call(a),
            Name: lambda a: a.id,
            Attribute: lambda a: self.process_attribute(a),
            Constant: lambda a: self.process_constant(a),
            UnaryOp: lambda a: self.process_unary_op(a),
            # BinOp: lambda a: self.process_bin_op(a),
            Compare: lambda a: self.process_compare(a),
            BoolOp: lambda a: self.process_bool_op(a),
            Lambda: lambda a: self.parse_lambda(a),
            JoinedStr: lambda a: self.process_joined_string(a),

            Tuple: lambda a: self.parse_tuple(a),
            List: lambda a: self.parse_list(a),
            Dict: lambda a: self.parse_dict(a),
            Set: lambda a: self.parse_set(a),

            Subscript: lambda a: self.process_subscript(a),

            Starred: lambda a: f"**{a.value.id}"
        }
        if type(a) == BinOp:
            if type(a.op) == Mult:
                return self.process_bin_op(a)
            return self.process_bin_op(a)
        else:
            return case_switch.get(type(a), lambda a: self.throw(f"NOT YET IMPLEMENTED: {type(a)}"))(a)

    def process_bool_op(self, arg):
        if type(arg.op) == Or:
            return f"{self.process_statement(arg.values[0])} {OR} {self.process_statement(arg.values[1])}"
        elif type(arg.op) == And:
            return f"{self.process_statement(arg.values[0])} {AND} {self.process_statement(arg.values[1])}"
        elif type(arg.op) == Not:
            return f"{NOT} {self.process_statement(arg.operand)}"
        else:
            breakpoint()
            raise Exception("BoolOp and ternary...")

    def process_attribute(self, body, s: str = ""):
        if type(body.value) == Call:
            return self.process_attribute_call(body.value)
        last_attr = body.attr
        if type(body.value) == Name:
            if self.config.debug: print(f"{body.value} IS A NAME... NO RECURSION...")
            v = body.value.id
            s = self.config._self + s if v == 'self' else v + s
        else:
            if self.config.debug: print("NOW RECURSING...")
            s = self.process_attribute(body.value, s) + s
        s += "." + last_attr
        return s

    def process_chained_call(self, call, s: str = ""):
        return self.process_attribute_call(call, s=s)

    def process_attribute_call(self, call, s: str = ""):
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
                s = self.parse_list(call.func.value) + s
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

    def process_named_call(self, call):
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
                return ""
            except IndexError:
                raise Exception("EMPTY DICT???")

        if function_name == 'ternary':
            return self.process_ternary(call)

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
            args_string += ", ".join([self.process_arg(arg) for arg in args[1:]]) if first_arg_id == 'dict' else ', '.join([self.process_arg(arg) for arg in args])

        kwargs = call.keywords
        if first_arg_id == 'dict':
            kwargs.extend(args[0].keywords)
        kwargs_string = ''
        if kwargs and not [kw.arg for kw in kwargs if kw.arg == 'content']:
            kwargs_string += ', '

        if self.inside_return and ((function_name.lower() in ['div', 'ul', 'ol', 'li', 'p', 'route']) or (function_name in self.imported_components)):
            # HTML TAG CASE or IMPORTED REACT COMPONENT CASE
            close1, close2 = ('/', '') if function_name.lower() in self_closing_tags else ('', f'</{function_name}>')
            if content:
                actual_contents = [kw.value for kw in kwargs if kw.arg == 'content'][0]
                kwargs_string += ", ".join([f"{kw.arg}={self.process_arg(kw.value)}" for kw in kwargs if not kw.arg == 'content'])
                return f"<{function_name}{kwargs_string.replace(', ', ' ')}{close1}>{self.process_statement(actual_contents)}{close2}"
            else:
                kwargs_string += ", ".join([f"{kw.arg}={self.process_arg(kw.value)}" for kw in kwargs])
                if "True" in kwargs_string:
                    kwargs_string = kwargs_string.replace('="True"', '')
                return f"<{function_name}{kwargs_string.replace(', ', ' ')}{close1}>{args_string}{close2}"
        else:
            return f"{function_name}({args_string}{kwargs_string})"

    def parse_dict(self, d):
        dict_body = self.config.dict_sep.join([f"{self.process_constant(key) if type(key) == Constant else key.id}: {self.process_arg(val)}" for key, val in zip(d.keys, d.values)])
        return f"{self.config.dict_wrapper[0]} {dict_body} {self.config.dict_wrapper[1]}"

    def parse_set(self, s):
        result = self.config.set_sep.join([self.process_arg(el) for el in s.elts])
        return f"{self.config.set_wrapper[0]}{result}{self.config.set_wrapper[1]}"

    def parse_list(self, l):
        result = self.config.list_sep.join([self.process_statement(el) for el in l.elts])
        return f"[{result}]"

    def parse_tuple(self, t):
        result = ", ".join([self.process_arg(v) for v in t.elts])
        return f"{self.config.tuple_wrapper[0]}{result}{self.config.tuple_wrapper[1]}"

    def process_target(self, t):
        case_switch = {
            Name: lambda t: self.process_name(t),
            Attribute: lambda t: self.process_attribute(t),
            Tuple: lambda t: self.parse_tuple(t),
            List: lambda t: self.parse_list(t)
        }
        return case_switch.get(type(t), lambda t: self.throw(f"NOT YET IMPLEMENTED: {type(t)}"))(t)

    @return_func
    def parse_return(self, r):
        ## NOTE: LOTS OF SPECIAL CASES FOR REACT... ##
        if self.config.debug: print("RETURN")
        expr = r.value
        if type(expr) == Tuple:
            raise Exception(f"TODO: Return of {str(expr)}")
        if expr == None:
            if self.config.debug: print("Function returns nothing.")
            expr = ""
        else:
            expr = self.process_statement(expr)
        return f"return {self.config.wrap_return[0]}{expr}{self.config.wrap_return[1]}{self.config.end_statement}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_assign(self, e, augment = False):
        augment_string = '+' if augment else ''
        # TODO: Handle reassignment to already declared consts/vars... #
        ## Note that this may involve some kind of DIY stack trace implementation to keep track of local variables... ##
        # TODO: Proper handling of semicolons at the end of statements... #

        ## TODO: Also, multiple assignments in same statement...
        if self.config.debug: print("ASSIGN")
        targets = ", ".join([self.process_target(t) for t in e.targets]) if not augment else self.process_statement(e.target)
        val = self.process_statement(e.value)
        new = 'new ' if type(e.value) == Call else ''
        if 'this' in targets:
            return f"{targets} {augment_string}= {new}{val}"
        else:
            if augment or targets.strip() in self.config.assign_special_cases: return f"{targets} {augment_string}= {new}{val}"
            else: return f"{self.config.assign} {targets} {augment_string}= {new}{val}"

    def process_subscript(self, e):
        try:
            return f"{e.value.id}[{e.slice.id}]"
        except:
            try:
                return f"{self.process_statement(e.value)}[{self.process_statement(e.slice)}]"
            except:
                raise Exception("NOT YET IMPLEMENTED FOR SUBSCRIPT...")

    def process_name(self, e):
        return e.id

    def check_call(self, c):
        return f"{c}" if self.direct_parent[0] in ['JoinedStr', 'lambda'] else c

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_statement(self, statement, cls: bool = False):
        e = statement
        e_type = type(e)
        case_switch = {
            Assign: lambda e: self.process_assign(e),
            FunctionDef: lambda e: self.parse_function(e, cls=cls),
            Expr: lambda e: self.process_statement(e.value),
            Call: lambda e: self.check_call(self.process_call(e)),
            Return: lambda e: self.parse_return(e), # noqa
            Name: lambda e: self.process_name(e),
            Attribute: lambda e: self.process_attribute(e),
            Constant: lambda e: self.process_constant(e),
            If: lambda e: self.process_if(e),
            IfExp: lambda e: self.process_if(e),
            UnaryOp: lambda e: self.process_unary_op(e),
            BinOp: lambda e: self.process_bin_op(e),
            Compare: lambda e: self.process_compare(e),
            BoolOp: lambda e: self.process_bool_op(e),
            Lambda: lambda e: self.parse_lambda(e),
            JoinedStr: lambda e: self.process_joined_string(e),
            Subscript: lambda e: self.process_subscript(e),
            ClassDef: lambda e: self.process_cls(e),
            While: lambda e: self.process_while(e),
            AugAssign: lambda e: self.process_assign(e, augment=True),
            Tuple: lambda e: self.parse_tuple(e),

            Dict: lambda e: self.parse_dict(e),

            Pass: lambda e: ''
        }
        s = case_switch.get(e_type, lambda e: self.throw(f"NOT YET IMPLEMENTED: {e_type}"))(e)
        end_statement = ""
        if len(s) == 0:
            return ""
        return f"{s}{end_statement}"

    def process_while(self, e):
        return f"while ({self.process_compare(e.test)}) {{{N.join([self.process_statement(s) for s in e.body])}}}"

    def process_call(self, c):
        assert type(c) == Call
        if type(c) == JoinedStr: breakpoint()
        if type(c.func) == Call:
            return self.process_chained_call(c)
        return self.process_attribute_call(c) if type(c.func) == Attribute else self.process_named_call(c)

    def process_constant(self, e):
        case_switch = {
            int: lambda val: f"{val}",
            str: lambda val: f"\"{val}\"",
            type(...): lambda val: self.config._ellipsis,
            type(None): lambda val: self.config.none,
            float: lambda val: f"{val}"
        }
        val = e.value
        return case_switch.get(type(val), lambda val: self.throw(f"NOT YET IMPLEMENTED: {type(val)}"))(val)

    def process_unary_op(self, e):
        # unaryop = Invert | Not | UAdd | USub
        case_switch_dict = {
            USub: lambda e: f"-{self.process_statement(e.operand)}",
            Not: lambda e: f"!{self.process_statement(e.operand)}",
            UAdd: lambda e: f"+{self.process_statement(e.operand)}"
        }
        return case_switch_dict.get(type(e.op), lambda e: self.throw(f"NOT YET IMPLEMENTED: {type(e.op)}"))(e)

    def process_if(self, e):
        yo = N.join([self.process_statement(exp) for exp in e.body]) if type(e.body) == list else self.process_statement(e.body)
        self.direct_parent = ('conditional', None)
        if type(e.test) == Name:
            return f"if ({e.test.id}) {{{N + yo + N}}}"
        else:
            return f"if ({self.process_compare(e.test) if type(e.test) == Compare else self.process_bool_op(e.test)}) {{{N + yo + N}}}"

    def process_bin_op(self, body, double_and=False, special_long_lambda_case=False):
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
            return f"{left} {op} {right}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def parse_lambda(self, l):
        args, body = l.args, l.body
        args_string = ', '.join([str(arg.arg) for arg in args.args]) if args.args else ''
        self.direct_parent = ('lambda', None)
        if type(body) == BinOp:
            ## SPECIAL CASE FOR LONGER LAMBDAS IN PYTHON ##
            body_string = self.process_bin_op(body, special_long_lambda_case=True)
        else:
            body_string = self.process_statement(body)
        return f"{args_string} => {body_string}" if len(args.args) == 1 else f"({args_string}) => {body_string}"

    def process_joined_string(self, body):
        original_direct_parent = self.direct_parent[0], self.direct_parent[1]
        self.direct_parent = ('JoinedStr', None)
        s = "".join([val.value if type(val) == Constant else f"${{{self.process_statement(val.value)}}}" for val in body.values])
        self.direct_parent = original_direct_parent
        return f"`{s}`"

    def process_ternary(self, t):
        # Note: this is for my special ternary function I used to use until I became comfortable with the concept in both Python and JS
        # TODO: Process ACTUAL Python ternary operators like x if y else z
        if len(t.args) != 3:
            raise Exception("TERNARY BROKE")
        else:
            self.inside_custom_ternary = True
            arg1, arg2, arg3 = [self.process_arg(arg) for arg in t.args]
            self.inside_custom_ternary = False
            return f"{arg1} ? {arg2} : {arg3}"

    def parse_function(self, func, cls: bool = False):
        n_defaults = len(_defaults := func.args.defaults)
        _defaults = iter(_defaults)
        args = [arg for arg in func.args.args if arg.arg != 'self']
        n_args = len(args)
        defaults = [next(_defaults) if i >= n_args-n_defaults else None for i in range(n_args)]
        arg_string = ', '.join([self.process_funcdef_arg(arg, default) for arg, default in zip(args, defaults)])
        returns = ' -> ' + self.process_statement(func.returns) if func.returns else ''
        ## TODO: decorators = "\n".join([f"@{self.process_statement(decorator)}" for decorator in func.decorator_list]) if func.decorator_list else ""
        func_name = 'constructor' if func.name == '__init__' else func.name
        func_prefix = '' if cls or self.direct_parent[0] == 'cls' else 'function '
        self.direct_parent = ('func', func_name)
        body = self.process_body(func.body)
        return f"{func_prefix}{func_name} ({arg_string}){returns} {{ {body} }}"

    def process_funcdef_arg(self, a, default = None):
        hint = ': ' + self.process_statement(a.annotation) if a.annotation else ''
        default = ' = ' + self.process_statement(default) if default else ''
        return f"{a.arg}{hint}{default}"

    @pre_hook_wrapper
    @post_hook_wrapper
    def process_cls(self, cls):
        self.direct_parent = ('cls', cls.name)
        body = self.process_body(cls.body, cls=True)
        inherits = ''
        return f"class {cls.name}{inherits} {{{body}}}"

    def throw(self, e: str):
        raise Exception(e)

