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
    def _process_assign(self, e, augment = False) -> str:
        augment_string = ""
        if augment:
            op_type = type(e.op)
            if op_type == ast.FloorDiv:
                # Remember that `//` is singe line comment notation in JavaScript, so we'll have to process this expression into a regular floor division (Math.floor()).
                # This *could* potentially lead to some very strange, albeit very rare, edge cases.
                return f"{e.target.id} = Math.floor({e.target.id} / {self.process_statement(e.value)})"
            augment_string = augment_op_dict.get(op_type, lambda e: self.throw(f"NOT YET IMPLEMENTED: {op_type}"))(e.op)

        targets = ", ".join([self.process_target(t) for t in e.targets]) if not augment else self.process_statement(e.target)
        if type(e.value) == ast.Call:
            is_defined = self.is_already_defined(e.value.func.id)
        else:
            is_defined = False
        new = 'new ' if type(e.value) == Call and not is_defined else ''
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
                actual_dict = ast.Dict(keys=keys, values=values)
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
        #breakpoint()
        if 'this' in targets:
            return f"{targets} {augment_string}= {new}{val}"
        else:
            if augment or targets.strip() in self.config.assign_special_cases: return f"{targets} {augment_string}= {new}{val}"
            else: return f"{assign} {targets} {augment_string}= {new}{val}"