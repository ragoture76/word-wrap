"""Core wrapping logic for the word_wrap package.

Design decisions (stated plainly so the behaviour is unambiguous):

1. Indentation is detected per logical line. The leading whitespace of each
   input line is measured; that exact prefix is reapplied to every wrapped
   continuation line produced from that input line. We do NOT try to
   re-indent based on nested structure, hanging indents, or list markers.
   One rule, applied uniformly.

2. A "word" is a maximal run of non-whitespace characters. We split on runs
   of whitespace (str.split() semantics), so multiple spaces between words
   collapse to a single space in the output. This is the trade-off for a
   simple, predictable wrapper: we preserve indentation, not inter-word
   spacing.

3. A single word longer than the available width is placed on its own line
   and allowed to overflow. We do not break words. If you need character
   breaking, this is not the right library.

4. Blank input lines are preserved as blank lines (with no indentation
   applied, since there is no content to indent).

5. width must be a positive integer. We validate up front rather than
   producing surprising output for width=0.
"""

from __future__ import annotations


def _leading_indent(line: str) -> str:
    """Return the leading whitespace of a line.

    We expand tabs to 4 spaces before measuring so that mixed tab/space
    indentation is normalised. The expansion width of 4 is a deliberate,
    fixed choice; we do not try to read tab-stop settings from the
    environment because that would make output non-deterministic across
    machines.
    """
    expanded = line.expandtabs(4)
    stripped = expanded.lstrip(" ")
    return expanded[: len(expanded) - len(stripped)]


def _wrap_single_line(line: str, width: int) -> list[str]:
    """Wrap one logical line (no internal newlines) to `width`.

    Returns a list of output lines. The indentation of the input line is
    preserved on every output line.
    """
    indent = _leading_indent(line)
    content = line[len(indent):] if line.startswith(indent) else line.lstrip()

    # A genuinely blank line: emit a single empty line, no indent.
    if not content:
        return [""]

    words = content.split()
    if not words:
        return [""]

    avail = width - len(indent)
    if avail <= 0:
        # The indentation alone meets or exceeds the width. We cannot fit
        # any word on an indented line within `width`, so we place each word
        # on its own line with the indent applied and let it overflow.
        # This is the only sensible option that preserves indentation.
        return [indent + w for w in words]

    lines: list[str] = []
    current = indent
    current_len = len(indent)

    for word in words:
        word_len = len(word)
        if current_len == len(indent):
            # First word on this line.
            current += word
            current_len += word_len
        else:
            # Would adding a space + word stay within width?
            if current_len + 1 + word_len <= width:
                current += " " + word
                current_len += 1 + word_len
            else:
                lines.append(current)
                current = indent + word
                current_len = len(indent) + word_len

    lines.append(current)
    return lines


def wrap_text(text: str, width: int) -> str:
    """Wrap `text` to `width` columns, honouring per-line indentation.

    Args:
        text: The input text. May contain multiple lines separated by "\n".
        width: The target column width. Must be a positive integer.

    Returns:
        The wrapped text as a single string with "\n" line separators.

    Raises:
        ValueError: If `width` is not a positive integer.
    """
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        raise ValueError(f"width must be a positive integer, got {width!r}")

    if text == "":
        return ""

    out_lines: list[str] = []
    for raw_line in text.split("\n"):
        out_lines.extend(_wrap_single_line(raw_line, width))
    return "\n".join(out_lines)


def wrap(text: str, width: int) -> str:
    """Alias for :func:`wrap_text`.

    Provided as a shorter, more discoverable name for the primary entry
    point.
    """
    return wrap_text(text, width)
