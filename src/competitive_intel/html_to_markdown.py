"""Turn public HTML into markdown for Knowledge Cards. No PDF download."""

from __future__ import annotations

import json
import re
from html import unescape
from html.parser import HTMLParser


class _HTMLText(HTMLParser):
    """Walk HTML and keep headings, paragraphs, and list items."""

    SKIP = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._buf: list[str] = []
        self._chunk = ""
        self._tag = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in {"h1", "h2", "h3", "h4", "p", "li"}:
            self._flush()
            self._tag = tag
        if tag == "br":
            self._chunk += "\n"

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in {"h1", "h2", "h3", "h4", "p", "li"}:
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        self._chunk += data

    def _flush(self) -> None:
        text = re.sub(r"\s+", " ", unescape(self._chunk)).strip()
        if text:
            if self._tag == "h1":
                self._buf.append(f"# {text}")
            elif self._tag == "h2":
                self._buf.append(f"## {text}")
            elif self._tag == "h3":
                self._buf.append(f"### {text}")
            elif self._tag == "h4":
                self._buf.append(f"#### {text}")
            elif self._tag == "li":
                self._buf.append(f"- {text}")
            else:
                self._buf.append(text)
        self._chunk = ""
        self._tag = ""

    def text(self) -> str:
        self._flush()
        return "\n\n".join(self._buf)


def html_to_markdown(html: str) -> str:
    """Return readable markdown from an HTML page body."""
    if not html or not html.strip():
        raise ValueError("html is required")
    parser = _HTMLText()
    parser.feed(html)
    body = parser.text()
    extras: list[str] = []
    for block in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        flags=re.I | re.S,
    ):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        extras.extend(_questions_from_jsonld(data))
    if extras:
        body = body + "\n\n## Extracted FAQ questions\n\n" + "\n".join(
            f"- {item}" for item in extras
        )
    if len(body.strip()) < 40:
        raise ValueError("html produced no usable text")
    return body


def _questions_from_jsonld(data: object) -> list[str]:
    found: list[str] = []
    if isinstance(data, list):
        for item in data:
            found.extend(_questions_from_jsonld(item))
        return found
    if not isinstance(data, dict):
        return found
    if data.get("@type") == "Question" and data.get("name"):
        found.append(str(data["name"]).strip())
    answer = data.get("acceptedAnswer")
    if isinstance(answer, dict) and answer.get("text"):
        found.append(str(answer["text"]).strip())
    for key in ("mainEntity", "@graph"):
        if key in data:
            found.extend(_questions_from_jsonld(data[key]))
    return found
