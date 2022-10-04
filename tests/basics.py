import sys
import os
sys.path.append(os.getcwd())

import subprocess

from main import Main

def test_simple_string_no_run(js: str = None):
    js = js if js else '''
print("Hello World")
    '''
    js = Main(js)
    s = js.transpile()
    print(s)





def test_simple_string_with_run(js: str = None):
    js = js if js else '''
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
    #exec(s)

    with open('tests/testout/scripts/test.js', 'w') as f:
        f.write(s)

    p = subprocess.Popen(['node', 'tests/testout/scripts/test.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.read()
    print(out)
    err = p.stderr.read()
    print(err)



def test_loaded_file_with_run(file_path: str):
    js = Main(open(file_path, 'r').read())
    s = js.transpile()
    print(s)
    # exec(s)

    with open('tests/testout/scripts/test.js', 'w') as f:
        f.write(s)

    p = subprocess.Popen(['node', 'tests/testout/scripts/test.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.read()
    print(out)
    err = p.stderr.read()
    print(err)


test_loaded_file_with_run('tests/vanillajs/basicsyntax.py')


