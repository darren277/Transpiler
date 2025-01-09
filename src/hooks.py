""""""

body_types = []
attribute_call_types = []
funcdef_arg_types = []

function_types = []
call_types = []
arg_types = []
assign_types = []
named_call_types = []
constant_types = []
attribute_types = []
bin_op_types = []
compare_types = []
unary_op_types = []
bool_op_types = []
lambda_types = []
target_types = []
if_types = []
try_types = []
cls_types = []
except_types = []
joined_string_types = []
for_loop_types = []




class Hooks:
    def pre_hook(self, loc):
        func_name = loc['func'].__name__
        if func_name == 'process_statement':
            ...
        elif func_name == 'process_body':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_body")
            body_types.extend(['ast.'+type(arg).__name__ for arg in loc['args'][0]])
        elif func_name == 'process_attribute_call':
            if len(loc['args']) > 2: raise ValueError("Too many arguments for process_attribute_call")
            attribute_call_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_funcdef_arg':
            if len(loc['args']) > 2: raise ValueError("Too many arguments for process_funcdef_arg")
            funcdef_arg_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])

        elif func_name == 'process_function':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_function")
            function_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_call':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_call")
            call_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_arg':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_arg")
            arg_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_assign':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_assign")
            assign_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_named_call':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_named_call")
            named_call_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_constant':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_constant")
            constant_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_attribute':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_attribute")
            attribute_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_bin_op':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_bin_op")
            bin_op_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_compare':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_compare")
            compare_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_unary_op':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_unary_op")
            unary_op_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_bool_op':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_bool_op")
            bool_op_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_lambda':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_lambda")
            lambda_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_target':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_target")
            target_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_if':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_if")
            if_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_try':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_try")
            try_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_cls':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_cls")
            cls_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_except':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_except")
            except_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_joined_string':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_joined_string")
            joined_string_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        elif func_name == 'process_for_loop':
            if len(loc['args']) > 1: raise ValueError("Too many arguments for process_for_loop")
            for_loop_types.extend(['ast.'+type(arg).__name__ for arg in loc['args']])
        else:
            print("ABOUT TO CALL: ", func_name)
            print("TAKING IN THE FOLLOWING ARGUMENT TYPES: ", loc['args'])
        func_name = loc['func'].__name__
        e = loc['args'][0]
        #print("PRE HOOK", func_name, e, loc)
        #print(convert_back_to_code(self.code, e))

        #print("BODY TYPES:", set(body_types))
        #print("ATTRIBUTE CALL TYPES:", set(attribute_call_types))
        #print("FUNCDEF ARG TYPES:", set(funcdef_arg_types))

        #print("FUNCTION TYPES:", set(function_types))
        #print("CALL TYPES:", set(call_types))
        #print("ARG TYPES:", set(arg_types))
        #print("PROCESS ASSIGN:", set(assign_types))
        #print("NAMED CALL TYPES:", set(named_call_types))
        #print("CONSTANT TYPES:", set(constant_types))
        #print("ATTRIBUTE TYPES:", set(attribute_types))
        #print("BIN OP TYPES:", set(bin_op_types))
        #print("COMPARE TYPES:", set(compare_types))
        #print("UNARY OP TYPES:", set(unary_op_types))
        #print("BOOL OP TYPES:", set(bool_op_types))
        #print("LAMBDA TYPES:", set(lambda_types))
        #print("TARGET TYPES:", set(target_types))
        #print("IF TYPES:", set(if_types))
        #print("TRY TYPES:", set(try_types))
        #print("CLS TYPES:", set(cls_types))
        #print("EXCEPT TYPES:", set(except_types))
        #print("JOINED STRING TYPES:", set(joined_string_types))
        #print("FOR LOOP TYPES:", set(for_loop_types))

    def post_hook(self, loc):
        #print("POST HOOK", loc['func'].__name__, loc['args'][0], loc)
        ...
