from main import Code

js = '''
print("Hello World")
'''

js = Code(js)

s = js.transpile()
print(s)




## TODO: The semicolon problem... ##
js = '''
def test():
    print("Hello World")

test()

class Test:
    def __init__(self):
        pass

    def test(self):
        print("Hello World")

t = Test()
t.test()
'''
js = Code(js)

s = js.transpile()
print(s)




