""""""

# Functions #

## Simple function ##
def hello_world():
    print("Hello World!")

## Simple function with parameters ##
def hello_you(name):
    print("Hello " + name)

## Simple function with parameters and return value ##
def hello_there(name):
    return "Hello " + name


# Binary Operations #

## Simple addition ##
def add(a, b):
    return a + b

## Simple subtraction ##
def subtract(a, b):
    return a - b

## Simple multiplication ##
def multiply(a, b):
    return a * b

## Simple division ##
def divide(a, b):
    return a / b

## Simple modulo ##
def modulo(a, b):
    return a % b

## Simple exponentiation ##
def exponentiate(a, b):
    return a ** b

## Simple floor division ##
def floor_divide(a, b):
    return a // b

## Simple bitwise AND ##
def bitwise_and(a, b):
    return a & b

## Simple bitwise OR ##
def bitwise_or(a, b):
    return a | b

## Simple bitwise XOR ##
def bitwise_xor(a, b):
    return a ^ b

## Simple bitwise NOT ##
def bitwise_not(a):
    return ~a

## Simple bitwise left shift ##
def bitwise_left_shift(a, b):
    return a << b

## Simple bitwise right shift ##
def bitwise_right_shift(a, b):
    return a >> b

## Simple bitwise left rotate ##
def bitwise_left_rotate(a, b):
    return a.rotl(b)

## Simple bitwise right rotate ##
def bitwise_right_rotate(a, b):
    return a.rotr(b)


# Boolean Operations #

## Simple AND ##
def boolean_and(a, b):
    return a and b

## Simple OR ##
def boolean_or(a, b):
    return a or b

## Simple NOT ##
def boolean_not(a):
    return not a

## Simple XOR ##
def boolean_xor(a, b):
    return a ^ b

## Simple NAND ##
def boolean_nand(a, b):
    return not (a and b)

## Simple NOR ##
def boolean_nor(a, b):
    return not (a or b)

## Simple XNOR ##
def boolean_xnor(a, b):
    return not (a ^ b)


# Comparison Operations #

## Simple equality ##
def equality(a, b):
    return a == b

## Simple inequality ##
def inequality(a, b):
    return a != b

## Simple less than ##
def less_than(a, b):
    return a < b

## Simple less than or equal to ##
def less_than_or_equal_to(a, b):
    return a <= b

## Simple greater than ##
def greater_than(a, b):
    return a > b

## Simple greater than or equal to ##
def greater_than_or_equal_to(a, b):
    return a >= b


# Assignment #

## Simple assignment ##
def assign(a):
    x = a
    return x

## Simple addition assignment ##
def add_assign(a, b):
    a += b
    return a

## Simple subtraction assignment ##
def subtract_assign(a, b):
    a -= b
    return a

## Simple multiplication assignment ##
def multiply_assign(a, b):
    a *= b
    return a

## Simple division assignment ##
def divide_assign(a, b):
    a /= b
    return a

## Simple modulo assignment ##
def modulo_assign(a, b):
    a %= b
    return a

## Simple exponentiation assignment ##
def exponentiate_assign(a, b):
    a **= b
    return a

## Simple floor division assignment ##
def floor_divide_assign(a, b):
    a //= b
    return a

## Simple bitwise AND assignment ##
def bitwise_and_assign(a, b):
    a &= b
    return a

## Simple bitwise OR assignment ##
def bitwise_or_assign(a, b):
    a |= b
    return a

## Simple bitwise XOR assignment ##
def bitwise_xor_assign(a, b):
    a ^= b
    return a

## Simple bitwise left shift assignment ##
def bitwise_left_shift_assign(a, b):
    a <<= b
    return a

## Simple bitwise right shift assignment ##
def bitwise_right_shift_assign(a, b):
    a >>= b
    return a




# Data Structures #

## Arrays ##
my_array = [1, 2, 3, 4, 5]

## Dictionaries/Objects ##
my_dict = {'key1': 'value1', 'key2': 'value2'}
my_other_dict = dict(key1='value1', key2='value2')

## Sets ##
my_set = {1, 2, 3, 4, 5}
my_set.add(6)

## Tuples... oh, wait... ##
my_tuple = (1, 2, 3, 4, 5)


# Control Flow #

## If/Else ##
if 1 == 1:
    print("1 is equal to 1")

## If/Else/Elif ##
if 1 == 1:
    print("1 is equal to 1")
elif 1 == 2:
    print("1 is equal to 2")
else:
    print("1 is not equal to 1 or 2")


## For Loops ##
for i in range(0, 10):
    print(i)

## While Loops ##
# NOTE: To ensure that this is declared as a `var` and not a `const`, I changed the default assignment to `var`.
# I also added a new set of special types, so you could alternatively set the default to `const` or even `let` and then override like so:
# i = var(0)
i = 0
while i < 10:
    print(i)
    i += 1

## Case Switch ##
def case_switch(a):
    switcher = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five"
    }
    return switcher.get(a, "Invalid number")

## Case Switch with Logic ##
def case_switch_with_logic(a):
    switcher = {
        1: lambda x: x + 1,
        2: lambda x: x + 2,
        3: lambda x: x + 3,
        4: lambda x: x + 4,
        5: lambda x: x + 5
    }
    return switcher.get(a, lambda x: "Invalid number")

## Try/Except ##
try:
    print(1 / 0)
except ZeroDivisionError:
    print("You can't divide by zero!")





# Classes #

## Simple Class ##
class MyClass:
    def __init__(self):
        self.my_var = "Hello World!"

    def my_function(self):
        print(self.my_var)

## Class with Inheritance ##
class MyOtherClass(MyClass):
    def __init__(self):
        super(MyClass)#.__init__()
        self.my_other_var = "Hello World!"

    def my_other_function(self):
        print(self.my_other_var)

## Class with Static Method ##
class MyStaticClass:
    @staticmethod
    def my_static_function():
        print("Hello World!")

## Class with Class Method ##
class MyClassMethod:
    @classmethod
    def my_class_method(cls):
        print("Hello World!")

## Class with Property ##
class MyPropertyClass:
    def __init__(self):
        self._my_property = "Hello World!"

    @property
    def my_property(self):
        return self._my_property

    @my_property.setter
    def my_property(self, value):
        self._my_property = value



# Other #

## String formatting ##
val = 'World'
print(f"Hello, {val}!")



## Anonymous/Lambda functions ##

f1 = lambda: "Hello World!"

f2 = lambda x: x + 1

f3 = lambda x, y: x + y



my_special_var = var(25)
my_special_const = const(25)
my_special_let = let(25)

# TODO: Multiple assignment...
# e.g. x, y, z = var(20, 40, 60)





## Ternary ##
a = 1 if 1 == 1 else 2



# Comprehensions #

## List Comprehensions ##
my_list = [i for i in range(0, 10)]

## Dictionary Comprehensions ##
my_dict = {i: i for i in range(0, 10)}

## Set Comprehensions ##
my_set = {i for i in range(0, 10)}

