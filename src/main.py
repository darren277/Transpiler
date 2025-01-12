""""""
import ast
import inspect

from config import ASTConfig, DEFAULT_CONFIG


class Code:
    react = True

    def __init__(self, code: str or callable, config: ASTConfig = DEFAULT_CONFIG, config_kwargs: dict = None):
        self.code = code if type(code) == str else inspect.getsource(code)
        self.imported_components = []
        self.import_lines = []

        self.self_closing_tags = ['route']

        if config_kwargs:
            config.update(config_kwargs)

        self.inside_return = False; self.inside_custom_ternary = False

        lines = self.code.splitlines()

        self.imports = [self.parse_import(line) for line in lines if ('_import' in line) or line.startswith('import') or line.startswith('from')]
        self.code = "\n".join([line for line in lines if not (('_import' in line) or line.startswith('import') or line.startswith('from'))])
        self.ast = ast.parse(self.code)

        self.direct_parent = (None, None)

        # Currently placed after IF statements and ASSIGNS... #
        self.eos = ';'

        self.config = config
        self.react = self.config.react

        self.log_file = None
        self.log_file = config.log_file
