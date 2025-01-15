""""""

class ComponentWithProps(React.Component):
    def __init__(self, props):
        #TODO: (currently automatically injecting) super().__init__(props)
        self.props = props

    def render(self):
        return (div({self.props.author.name}, className="App"))


# class Welcome extends React.Component
class ComponentWithState(React.Component):
    def __init__(self):
        self.state = {
            "name": "John",
            "age": 30
        }

    def changeName(self, name):
        self.setState({"name": name})

    def render(self):
        return (
            div(
                h1(f"Hello {self.state['name']}"),
                h1(f"Your age: {self.state['age']}"),
                button("Change name", onClick=lambda: self.changeName("Bob")),
                button("Change age", onClick=lambda: self.setState({"age": 50})),
            )
        )

class App(React.Component):
    def render(self):
        return (
            div(
                ComponentWithProps(author={'name': 'Jeff'}),
                ComponentWithState()
            )
        )
