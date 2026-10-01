# Word Wrap

Wrap text to a fixed width while preserving the leading indentation of each input line.

## Usage

```python
from word_wrap import wrap

result = wrap("    alpha beta gamma delta epsilon zeta", 20)
print(result)
#     alpha beta gamma
#     delta epsilon
```

The two exported names are `wrap` and `wrap_text`; they are the same function under two names.

## Why this exists

Most text wrappers either ignore indentation entirely or try to be clever about hanging indents, list markers, and nested structure. The clever ones break in surprising ways. This library does one thing: it reads the leading whitespace of each input line and reapplies that exact prefix to every wrapped continuation line produced from that line. No re-indentation logic, no structure detection.

The trade-off is that multiple spaces between words collapse to a single space in the output (words are split on whitespace runs). If you need to preserve inter-word spacing, this is not the right tool.

## Edges you will hit

- A single word longer than the available width is placed on its own line and allowed to overflow. Words are never broken.
- If the indentation itself is wider than `width`, each word gets its own indented line and overflows. There is no fallback to dropping the indent.
- Tabs in leading whitespace are expanded to 4 spaces before measuring. This is fixed, not configurable.
- `width` must be a positive integer. `bool` is rejected even though it is a subclass of `int`.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
