""""""
from settings import LOG_FILE

class ASTConfig:
    def __init__(self, assign: str = 'let', wrap_return: str = "", tuples_in_curly_braces: bool = True, tuples_in_square_brackets: bool = False,
                 debug: bool = False, log_file: str = LOG_FILE, react_app: bool = False, do_print_code: bool = False):
        self.react_app = react_app

        self.assign = assign
        self.wrap_return = wrap_return
        self.tuples_in_curly_braces = tuples_in_curly_braces
        self.tuples_in_square_brackets = tuples_in_square_brackets

        self.debug = debug

        self.assign = 'const'
        self.assign = 'var'
        self.assign = 'let'

        self.NOT = '!'
        self.AND = '&&'
        self.OR = '||'

        #self.wrap_return = "()"
        self.wrap_return = wrap_return
        self.list_sep = ", "
        self.set_sep = ","
        #self.set_wrapper = "[]"
        self.set_wrapper = ""
        self.dict_sep = ", "
        self.dict_wrapper = "{}"
        self.tuple_sep = ","
        self.tuple_wrapper = "[]"
        self._ellipsis = ""
        self.none = 'null'
        self._self = 'this'
        #self.end_statement = ';\n'
        #self.end_statement = '\n'
        self.end_statement = ''
        self.assign = assign
        # self.list_sep = config.list_sep

        self.react = True

        self.assign_special_cases = []

        if tuples_in_curly_braces and tuples_in_square_brackets:
            raise Exception("Make up your mind about the tuples!")

        self.tuples_in_curly_braces = tuples_in_curly_braces
        self.tuples_in_square_brackets = tuples_in_square_brackets

        self.log_file = log_file

        self.do_print_code = do_print_code

    def update(self, config_kwargs: dict):
        for key, val in config_kwargs.items():
            setattr(self, key, val)




DEFAULT_CONFIG = ASTConfig(debug=True)

