"""Tests for word_wrap.core.

Every test here corresponds to behaviour the implementation explicitly
claims to support. We test the awkward edges that the code actually
handles: blank lines, long words, indentation wider than width, multiple
spaces collapsing, and validation of the width argument.
"""

import unittest

from word_wrap import wrap, wrap_text


class TestWrapText(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(wrap_text("", 40), "")

    def test_single_line_short_no_wrap(self):
        self.assertEqual(wrap_text("hello world", 40), "hello world")

    def test_single_line_wraps_at_word_boundary(self):
        text = "alpha beta gamma delta epsilon"
        result = wrap_text(text, 18)
        # 18 cols: "alpha beta gamma" = 17, +" delta" = 23 -> overflow
        self.assertEqual(result, "alpha beta gamma\ndelta epsilon")

    def test_indentation_preserved_on_continuation(self):
        text = "    alpha beta gamma delta epsilon zeta"
        result = wrap_text(text, 20)
        lines = result.split("\n")
        self.assertEqual(lines[0], "    alpha beta gamma")
        self.assertEqual(lines[1], "    delta epsilon")
        # Every line must carry the 4-space indent.
        for ln in lines:
            self.assertTrue(ln.startswith("    "))

    def test_long_word_overflows_on_own_line(self):
        text = "short supercalifragilisticexpialidocious more"
        result = wrap_text(text, 10)
        # "short" fits (5), then the long word can't fit so it goes on its
        # own line and overflows. "more" follows on the next line.
        self.assertEqual(result, "short\nsupercalifragilisticexpialidocious\nmore")

    def test_long_word_with_indentation(self):
        text = "  ab supercalifragilisticexpialidocious cd"
        result = wrap_text(text, 10)
        lines = result.split("\n")
        self.assertEqual(lines[0], "  ab")
        self.assertEqual(lines[1], "  supercalifragilisticexpialidocious")
        self.assertEqual(lines[2], "  cd")

    def test_blank_line_preserved(self):
        text = "first line\n\nthird line"
        result = wrap_text(text, 40)
        self.assertEqual(result, "first line\n\nthird line")

    def test_multiple_blank_lines_preserved(self):
        text = "a\n\n\nb"
        result = wrap_text(text, 40)
        self.assertEqual(result, "a\n\n\nb")

    def test_multiple_spaces_collapse(self):
        text = "alpha   beta     gamma"
        result = wrap_text(text, 40)
        self.assertEqual(result, "alpha beta gamma")

    def test_indentation_only_line_becomes_blank(self):
        # A line that is only whitespace has no content words, so it is
        # treated as a blank line (empty output, no indent).
        text = "    \nnext"
        result = wrap_text(text, 40)
        self.assertEqual(result, "\nnext")

    def test_tab_indentation_expanded_to_four_spaces(self):
        text = "\talpha beta gamma delta"
        result = wrap_text(text, 16)
        lines = result.split("\n")
        # Tab expands to 4 spaces; indent is 4, avail is 12.
        # "alpha beta" = 10, +" gamma" = 16 -> exactly 16, fits.
        self.assertEqual(lines[0], "    alpha beta")
        self.assertEqual(lines[1], "    gamma delta")

    def test_indentation_wider_than_width(self):
        # Indent is 10 spaces, width is 8. avail <= 0, so each word goes
        # on its own line with the indent applied and overflows.
        text = "          alpha beta"
        result = wrap_text(text, 8)
        self.assertEqual(result, "          alpha\n          beta")

    def test_width_must_be_positive(self):
        with self.assertRaises(ValueError):
            wrap_text("hello", 0)

    def test_width_must_be_integer(self):
        with self.assertRaises(ValueError):
            wrap_text("hello", 3.5)

    def test_width_bool_rejected(self):
        # bool is a subclass of int but we reject it to avoid surprises.
        with self.assertRaises(ValueError):
            wrap_text("hello", True)

    def test_wrap_alias_matches_wrap_text(self):
        text = "alpha beta gamma delta epsilon"
        self.assertEqual(wrap(text, 18), wrap_text(text, 18))

    def test_trailing_newline_in_input(self):
        # "a\n" splits to ["a", ""], so output is "a\n".
        self.assertEqual(wrap_text("a\n", 40), "a\n")

    def test_exactly_at_width(self):
        # "hello world" is 11 chars; at width 11 it should not wrap.
        self.assertEqual(wrap_text("hello world", 11), "hello world")

    def test_one_past_width_wraps(self):
        # At width 10, "hello world" (11) must wrap.
        self.assertEqual(wrap_text("hello world", 10), "hello\nworld")


if __name__ == "__main__":
    unittest.main()
