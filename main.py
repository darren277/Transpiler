""""""
from src.hooks import Hooks
from src.logger import Logger
from src.main import Code
from src.parsing.main import Visitor


class Main(Code, Visitor, Hooks, Logger):
    def throw(self, e: str):
        raise Exception(e)

