""""""
import subprocess
import sys
import os
sys.path.append(os.getcwd())

from main import Main


def test_loaded_file_with_run(file_path: str or None, custom_string: str = None):
    if not custom_string:
        # NOTE: Be sure to run `make jsx-install` (aka: `cd tests/testout/jsx && npm install`) before running this test.
        js = Main(open(file_path, 'r').read())
        js.config.react_app = True
        s = js.transpile()
        print(s)
        # exec(s)
    else:
        s = custom_string

    with open('tests/testout/jsx/src/App.jsx', 'w') as f:
        f.write(s)

    p = subprocess.Popen('npm run start', stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='tests/testout/jsx', shell=True)
    out = p.stdout.read()
    print(out)
    err = p.stderr.read().decode()
    if err:
        print(err)
        exception = next(line for line in err.splitlines() if line.startswith('SyntaxError'))
        raise Exception(exception)
    print(err)


simple_app = '''
import React from 'react';

function App() {
  return <h1>Hello World!</h1>;
}
export default App;
'''

# TODO: Turn these into `sys.argv` type of conditional...
# Test `simple_app` to make sure the React and Node and Webpack infrastructure are working:
#test_loaded_file_with_run(None, simple_app)

#test_loaded_file_with_run('tests/jsx/classbased.py')
#test_loaded_file_with_run('tests/jsx/functionbased.py')



def transpile_file(root_path: str, file_path: str):
    js = Main(open(file_path, 'r').read())
    js.config.react_app = True
    js.config.wrap_return = "()"
    js.config.tuple_wrapper = "{}"

    js.register_event_handler('handleEditClick')
    js.register_event_handler('deleteUser')

    s = js.transpile()
    print(s)
    actual_file_path = file_path.replace(root_path, '').replace('.py', '.jsx').replace('\\', '/')

    # create subdir if it doesn't exist
    subdir = os.path.dirname(f'tests/testout/multifile/src{actual_file_path}')
    if not os.path.exists(subdir):
        os.makedirs(subdir)

    if 'index.jsx' in actual_file_path:
        actual_file_path = actual_file_path.replace('index.jsx', 'index.js')
    with open(f'tests/testout/multifile/src{actual_file_path}', 'w') as f:
        print("ABOUT TO WRITE:", f'tests/testout/multifile/src{actual_file_path}')
        f.write(s)

def multifile_test(path: str):
    import os

    # for file in os.listdir(path):
    #     if file.endswith('.py'):
    #         print(f"Testing {file}...")
    #         transpile_file(path, os.path.join(path, file))

    # recursive...
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                print(f"Testing {file}...")
                transpile_file(path, os.path.join(root, file))

    # prettify via CLI...
    p = subprocess.Popen('npm run prettier', stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='tests/testout/multifile', shell=True)
    out = p.stdout.read()
    print(out)
    err = p.stderr.read().decode()
    if err:
        print(err)
        exception = next(line for line in err.splitlines() if line.startswith('SyntaxError'))
        raise Exception(exception)
    print(err)

    # p = subprocess.Popen('npm run start', stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='tests/testout/multifile', shell=True)
    # out = p.stdout.read()
    # print(out)
    # err = p.stderr.read().decode()
    # if err:
    #     print(err)
    #     exception = next(line for line in err.splitlines() if line.startswith('SyntaxError'))
    #     raise Exception(exception)
    # print(err)

multifile_test('tests/jsx/multifile')
