""""""

class var:
    def __init__(self, val):
        self.val = val

class const:
    def __init__(self, val):
        self.val = val

class let:
    def __init__(self, val):
        self.val = val


def ternary(condition, true_val, false_val):
    return true_val if condition else false_val

