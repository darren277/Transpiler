import sys
import os
sys.path.append(os.getcwd())

from main import Main

js = '''
print("Hello World")
'''

js = Main(js)

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
js = Main(js)

s = js.transpile()
print(s)


import subprocess

with open('tests/testout/scripts/test.js', 'w') as f:
    f.write(s)

p = subprocess.Popen(['node', 'tests/testout/scripts/test.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = p.stdout.read()
print(out)
err = p.stderr.read()
print(err)





