""""""
import ast
from ast import *

N = '\n'


class IterablesVisitor:
    def _process_val(self, value, style: bool = False):
        if not style: return self.process_arg(value)
        else:
            if len(value.keys) > 1:
                return '{' + ', '.join([f'"{key.value}": {self.process_arg(val)}' for key, val in zip(value.keys, value.values)]) + '}'
            else:
                return self.process_arg(value)

    def _process_dict_key(self, key) -> str:
        if type(key) == Starred:
            return f"...{key.value.id}"
        if type(key) == List:
            return f"[{', '.join([self.process_arg(el) for el in key.elts])}]"
        if type(key) == Constant:
            if key.value == None:
                return ''
            return self.process_constant(key)
        elif hasattr(key, 'id'):
            return key.id
        elif type(key) == str:
            # NOTE: You have the option to wrap this in double quotes or even single quotes if desired.
            # TODO: Consider if wrapping in double quotes should be the default unless otherwise specified?
            return key
        elif type(key) == Subscript:
            return f'[{key.value.id}]'
        # Does this ever happen? else: breakpoint()

    def _process_dict(self, d) -> str:
        entries = []

        if len(d.keys) != len(d.values):
            raise Exception("Seriously!? This is a thing?")

        for key, value in zip(d.keys, d.values):
            processed_value = self.process_arg(value)

            if isinstance(key, ast.Starred):
                entries.append(self.process_dict_key(key))
            elif not key:
                entries.append(processed_value)
            elif isinstance(key, ast.Constant) and str(key.value) == 'Ellipsis':
                entries.append(f'...{processed_value}')
            else:
                processed_key = self.process_dict_key(key)
                entries.append(f"{processed_key}: {processed_value}")

        dict_body = self.config.dict_sep.join(entries)

        return f"{self.config.dict_wrapper[0]}{dict_body}{self.config.dict_wrapper[1]}"

    def _process_set(self, s) -> str:
        result = self.config.set_sep.join([self.process_arg(el) for el in s.elts])
        if len(self.config.set_wrapper) > 0 and not self.config.react_app:
            return f"new Set({self.config.set_wrapper[0]}{result}{self.config.set_wrapper[1]})"
        elif not self.config.react_app:
            return f"new Set([{result}])"
        elif self.config.react_app:
            return f"{{{result}}}"
        # Does this ever happen? else: raise Exception("process_set() case not yet implemented.")

    def _process_list(self, l) -> str:
        result = self.config.list_sep.join([self.process_statement(el) for el in l.elts])
        return f"[{result}]"

    def _process_tuple(self, t) -> str:
        result = ", ".join([self.process_arg(v) for v in t.elts])
        return f"{self.config.tuple_wrapper[0]}{result}{self.config.tuple_wrapper[1]}"

    def _process_list_comp(self, e) -> str:
        if len(e.generators) > 1: raise Exception("TODO: Multiple generators in list comprehension...")
        if len(e.generators[0].ifs): raise Exception("TODO: If statements in list comprehension...")
        if e.generators[0].is_async: raise Exception("TODO: Async list comprehension...")

        if type(e.elt) == Constant:
            return f"({self.process_statement(e.elt)} for {e.generators[0].target.id} in {self.process_statement(e.generators[0].iter)})"
        else:
            body = self.process_statement(e.elt.body)
            test = self.process_compare(e.elt.test) if type(e.elt.test) == Compare else self.process_arg(e.elt.test)
            orelse = self.process_statement(e.elt.orelse)
            elt = f"{{ if ({test}) {{ return ({body}) }} else {{ return ({orelse}) }} }}"
            return f"{e.generators[0].iter.id}.map(({e.generators[0].target.id}) => {elt})"

    def _process_dict_comp(self, e) -> str:
        if len(e.generators) > 1: raise Exception("TODO: Multiple generators in dict comprehension...")
        if len(e.generators[0].ifs): raise Exception("TODO: If statements in dict comprehension...")
        if e.generators[0].is_async: raise Exception("TODO: Async dict comprehension...")
        return f"{{ {self.process_statement(e.key)}: {self.process_statement(e.value)} for {e.generators[0].target.id} in {self.process_statement(e.generators[0].iter)} }}"

    def _process_set_comp(self, e) -> str:
        if len(e.generators) > 1: raise Exception("TODO: Multiple generators in set comprehension...")
        if len(e.generators[0].ifs): raise Exception("TODO: If statements in set comprehension...")
        if e.generators[0].is_async: raise Exception("TODO: Async set comprehension...")
        return f"{{ {self.process_statement(e.elt)} for {e.generators[0].target.id} in {self.process_statement(e.generators[0].iter)} }}"