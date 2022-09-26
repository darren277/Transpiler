from main import Code

js = '''
print("Hello World")
'''

js = Code(js)

s = js.transpile()
print(s)



