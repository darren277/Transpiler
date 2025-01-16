#from src.react import *

# TODO: Add a way to cut off imports above a certain line as they are only imported to get rid of the red squigglies in the editor.
# START HERE #

from src.react import useState, useEffect

def Header(props):
    headerTitle, setHeaderTitle = useState('')

    def onHeaderMount():
        print("Header mounted")
        setHeaderTitle(props.title)

    useEffect(lambda: onHeaderMount(), [])

    return div(
        h1(headerTitle),
        nav(
            a("Home", href="/"),
            a("Login", href="/login"),
            a("Signup", href="/signup"),
            a("Cart", href="/cart"),
            a("Orders", href="/orders"),
        )
    )

def Content():
    return (
        div(
            h1("Hello World!"),
            p("This is a paragraph."),
            a("This is a link.", href="https://www.google.com"),
            img(src="https://via.placeholder.com/150", alt="placeholder"),
            div(
                h2("This is a subheading."),
                p("This is a paragraph."),
                a("This is a link.", href="https://www.google.com"),
                img(src="https://via.placeholder.com/150", alt="placeholder"),
            )
        )
    )


def App():
    return (
        #div(routes(route(path='/', element=Fragment(Header(), Home()))), className="App")
        div(Fragment(Header(props={'title': 'Welcome to the Home Page'}), Content()), className="App")
    )

#export(default, App)
