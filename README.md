# TODO

## Testing

### Unit Tests

Run `pytest` from the CLI.

### Full Rendering Tests

#### Regular Syntax

Run `make test` for regular JS syntax testing.

#### JSX

Run `make test-jsx` for JSX syntax testing (and actual React component rendering).

Or, alternatively, navigate to the `tests/testout/jsx` directory and run `npm run start` to see the rendered React components in the browser.

## The semicolon problem

Apparently JavaScript automatically inserts semicolons in some cases.

The goal for this transpiler can be one of two:
1. Syntactical accuracy for theoretical correctness.
2. Minimal use of semicolons merely to ensure consistent behavior upon transpilation.

For now, I'm sticking with #2.

### 2025 SEMICOLON UPDATE

I made the official executive decision to just eliminate the semicolon altogether (except, of course, inside for loop instantiations).

The produced code looks so much nicer.

And, most importantly, modern JavaScript is just fine with it and everything runs without a hitch.

In fact, I've been noticing in other projects that TypeScript conventions tend to actually *insist* on avoiding semicolons.
