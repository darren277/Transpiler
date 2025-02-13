""""""

HTML_TAGS = [
    'div', 'ul', 'ol', 'li', 'p', 'button',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'nav', 'header', 'footer', 'main', 'section',
    'a', 'img', 'video', 'audio', 'iframe', 'canvas',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'input_', 'input', 'form', 'label', 'select', 'option',
    'route'
]

HTML_TAGS += [
    'App', 'React.StrictMode'
]

def div(*args, **kwargs): pass
def ul(*args, **kwargs): pass
def ol(*args, **kwargs): pass
def li(*args, **kwargs): pass
def p(*args, **kwargs): pass
def button(*args, **kwargs): pass
def h1(*args, **kwargs): pass
def h2(*args, **kwargs): pass
def h3(*args, **kwargs): pass
def h4(*args, **kwargs): pass
def h5(*args, **kwargs): pass
def h6(*args, **kwargs): pass
def nav(*args, **kwargs): pass
def header(*args, **kwargs): pass
def footer(*args, **kwargs): pass
def main(*args, **kwargs): pass
def section(*args, **kwargs): pass
def a(*args, **kwargs): pass
def img(*args, **kwargs): pass
def video(*args, **kwargs): pass
def audio(*args, **kwargs): pass
def iframe(*args, **kwargs): pass
def canvas(*args, **kwargs): pass
def route(*args, **kwargs): pass


def useState(initial_value):
    return initial_value

def useEffect(callback, dependencies):
    callback()

def Fragment(*args, **kwargs):
    pass


class React:
    Fragment = Fragment
