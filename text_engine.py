"""Find and safely edit visible text in the site's HTML files.

The approach: parse with html.parser in raw mode (convert_charrefs=False) so
every position it reports is an exact offset into the *original* file bytes.
Consecutive data/entity chunks between two tags are merged into one logical
text node, and we keep that node's raw start/end offset — not a reconstructed
string — so replacing it later touches nothing else in the file, byte for
byte.

Nodes are numbered in document order (seq 0, 1, 2, ...). That numbering is
recomputed fresh every time a file is parsed, so it only stays valid between
one read and the next write of the *same* file content — which is exactly
how this is used: read, maybe edit one node, write, done.
"""
import html
import os
from html.parser import HTMLParser

SKIP_SUBTREE = {"script", "style", "noscript", "template", "title", "svg"}
MIN_LEN = 2  # ignore stray single characters / pure punctuation


class _Node:
    __slots__ = ("seq", "tag", "start", "end", "raw", "text")

    def __init__(self, seq, tag, start, end, raw):
        self.seq = seq
        self.tag = tag
        self.start = start
        self.end = end
        self.raw = raw
        self.text = html.unescape(raw)

    def as_dict(self):
        return {"seq": self.seq, "tag": self.tag, "text": self.text}


class _Scanner(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.line_starts = self._line_starts(source)
        self.nodes = []
        self.in_body = False
        self.skip_depth = 0          # >0 while inside a SKIP_SUBTREE element
        self.tag_stack = []
        self.chunk_start = None      # abs offset where the current run of data began
        self.chunk_end = None

    @staticmethod
    def _line_starts(text):
        starts = [0]
        for i, ch in enumerate(text):
            if ch == "\n":
                starts.append(i + 1)
        return starts

    def _abs(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def _flush(self):
        if self.chunk_start is None or self.chunk_end is None:
            self.chunk_start = self.chunk_end = None
            return
        raw = self.source[self.chunk_start:self.chunk_end]
        # Trim to just the meaningful content, adjusting offsets to match, so
        # a replacement leaves the original surrounding indentation alone
        # and the editor doesn't show a wall of whitespace.
        lead = len(raw) - len(raw.lstrip())
        trail = len(raw) - len(raw.rstrip())
        start = self.chunk_start + lead
        end = self.chunk_end - trail
        trimmed = self.source[start:end] if end > start else ""

        text = html.unescape(trimmed)
        if len(text) >= MIN_LEN and self.skip_depth == 0 and self.in_body:
            tag = self.tag_stack[-1] if self.tag_stack else "body"
            self.nodes.append(_Node(len(self.nodes), tag, start, end, trimmed))
        self.chunk_start = self.chunk_end = None

    # -- tag handling --------------------------------------------------
    def handle_starttag(self, tag, attrs):
        self._flush()
        if tag == "body":
            self.in_body = True
        self.tag_stack.append(tag)
        if tag in SKIP_SUBTREE:
            self.skip_depth += 1

    def handle_startendtag(self, tag, attrs):
        self._flush()

    def handle_endtag(self, tag):
        self._flush()
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        if tag in SKIP_SUBTREE and self.skip_depth > 0:
            self.skip_depth -= 1
        if tag == "body":
            self.in_body = False

    def handle_comment(self, data):
        self._flush()

    def handle_decl(self, decl):
        self._flush()

    # -- data / entities, merged into the current run -------------------
    def handle_data(self, data):
        start = self._abs()
        end = start + len(data)
        if self.chunk_start is None:
            self.chunk_start = start
        self.chunk_end = end

    def handle_entityref(self, name):
        raw = f"&{name};"
        start = self._abs()
        end = start + len(raw)
        if self.chunk_start is None:
            self.chunk_start = start
        self.chunk_end = end

    def handle_charref(self, name):
        raw = f"&#{name};"
        start = self._abs()
        end = start + len(raw)
        if self.chunk_start is None:
            self.chunk_start = start
        self.chunk_end = end

    def close(self):
        self._flush()
        super().close()


def scan(source):
    """Return the list of editable text nodes, in document order."""
    p = _Scanner(source)
    p.feed(source)
    p.close()
    return p.nodes


def read(path):
    with open(path, encoding="utf-8", errors="surrogateescape", newline="") as fh:
        return fh.read()


def write(path, body):
    with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        fh.write(body)


def escape_for_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def apply_edit(path, seq, new_text):
    """Replace text node `seq` in the file at `path` with new_text. Returns the old text."""
    source = read(path)
    nodes = scan(source)
    target = next((n for n in nodes if n.seq == seq), None)
    if target is None:
        raise ValueError(f"No text node #{seq} in {path} (file may have changed)")
    escaped = escape_for_html(new_text)
    new_source = source[:target.start] + escaped + source[target.end:]
    write(path, new_source)
    return target.text
