""""""

class AppWithProps:
    def __init__(self, props):
        self.props = props

    def render(self):
        return (Div({self.props.author.name}, className="App"))


# class Welcome extends React.Component
class AppWithState(React.Component):
    def __init__(self):
        self.state = {
            "name": "John",
            "age": 30
        }

    def changeName(self, name):
        self.setState({"name": name})

    def render(self):
        return (
            Div(
                H1(f"Hello {self.state['name']}"),
                H1(f"Your age: {self.state['age']}"),
                Button("Change name", onClick=self.changeName("Bob")),
                Button("Change age", onClick=self.setState({"age": 50})),
            )
        )
