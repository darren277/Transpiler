""""""
from src.hooks import Hooks
from src.logging import Logging
from src.main import Code
from src.parsing.main import Visitor


class Main(Code, Visitor, Hooks, Logging):
    def throw(self, e: str):
        raise Exception(e)

