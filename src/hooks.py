""""""

class Hooks:
    def pre_hook(self, loc):
        func_name = loc['func'].__name__
        e = loc['args'][0]
        #print("PRE HOOK", func_name, e, loc)
        #print(convert_back_to_code(self.code, e))

    def post_hook(self, loc):
        #print("POST HOOK", loc['func'].__name__, loc['args'][0], loc)
        ...
