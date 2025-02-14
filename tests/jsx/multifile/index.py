import_('ReactDOM', _from='react-dom')
import_('{ StrictMode }', _from='react')
import_('App', _from='./App')
# import * as serviceWorker from './serviceWorker';
#import_('*', _as='serviceWorker', _from='./serviceWorker')

# ReactDOM.render(<StrictMode><App /></StrictMode>, document.getElementById("root"))
# This turns out to be a rather special case, as we are trying to render JSX but not inside of a return statement...
#ReactDOM.render(StrictMode(App), document.getElementById('root'))
PURE_STRING("ReactDOM.render(<StrictMode><App /></StrictMode>, document.getElementById('root'))")


# // If you want your app to work offline and load faster, you can change unregister() to register() below. Note this comes with some pitfalls.
# serviceWorker.unregister();
#serviceWorker.unregister()
