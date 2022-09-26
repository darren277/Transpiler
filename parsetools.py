""""""
import inspect
import types



def unindent_line(line: str):
    PREVIOUS_INDENT = 0

    if len(line) < 1:
        PREVIOUS_INDENT * chr(32)
        return line
    else:
        spaces = 0
        if ord(line[0]) == 32:
            for c in line:
                if ord(c) == 32:
                    spaces += 1
                else:
                    break
        return (spaces-4)*chr(32) + line.lstrip()



def unindent(code):
    return "\n".join([unindent_line(line) for line in code.splitlines()])




def analyze_class(cls):
    method_list = [func for func in dir(cls) if callable(getattr(cls, func)) and not func.startswith("__")]

    for method in method_list:
        print(method)
        print(locals())
        func = getattr(cls, method)
        print(type(func))
        if type(func) == types.FunctionType:
            source_foo = inspect.getsource(func)
            print(unindent(source_foo))


