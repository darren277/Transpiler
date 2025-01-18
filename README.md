# Transpiler

## About

This is a Python to JavaScript (or JSX) transpiler.

You write whatever code you want in Python, and then it converts it to fully executable JavaScript (or JSX) code.

It uses the `ast` (Abstract Syntax Tree) Python package for parsing Python code and constructing a syntax tree, then traversing that tree and generating JavaScript (or JSX) code as analogously as possible.

While it is currently at a point where it can handle the vast majority of syntax, there are still likely a few edge cases that will have to either be adapted towards by writing the Python code ever so slightly differently to accomodate JavaScript's stylistic differences, or via configuration parameters using the `ASTConfig` class and perhaps custom monkey patching on the user's part.

The current phase of the project consists of:
1. Continuously adding more robust testing, both in terms of unit testing of each individual parsing function, as well as large scale end to end JSX (i.e. React) rendering tests.
2. Refactoring the code base for better readability and customizability by other users.

## Testing

### Unit Tests

Run `pytest` from the CLI.

### Full Rendering Tests

#### Regular Syntax

Run `make test` for regular JS syntax testing.

#### JSX

Run `make test-jsx` for JSX syntax testing (and actual React component rendering).

Or, alternatively, navigate to the `tests/testout/jsx` directory and run `npm run start` to see the rendered React components in the browser.

## Assorted Notes

### The semicolon problem

Apparently JavaScript automatically inserts semicolons in some cases.

The goal for this transpiler can be one of two:
1. Syntactical accuracy for theoretical correctness.
2. Minimal use of semicolons merely to ensure consistent behavior upon transpilation.

For now, I'm sticking with #2.

#### 2025 SEMICOLON UPDATE

I made the official executive decision to just eliminate the semicolon altogether (except, of course, inside for loop instantiations).

The produced code looks so much nicer.

And, most importantly, modern JavaScript is just fine with it and everything runs without a hitch.

In fact, I've been noticing in other projects that TypeScript conventions tend to actually *insist* on avoiding semicolons.
