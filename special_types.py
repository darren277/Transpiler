""""""

class var:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return f"var {self.val}"

class const:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return f"const {self.val}"

class let:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return f"let {self.val}"


def ternary(condition, true_val, false_val):
    return true_val if condition else false_val


# import * as serviceWorker from './serviceWorker';
#import_('*', _as='serviceWorker', _from='./serviceWorker')

def import_(_as: str = None, _from: str = None):
    ...

