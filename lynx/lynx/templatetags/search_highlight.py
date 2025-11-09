from django import template
from django.utils.html import escape, mark_safe
import re

register = template.Library()

@register.filter
def highlight(text, tokens):
    """
    Escape `text` and wrap occurrences of any token (case-insensitive) in <mark class="search-hit">...</mark>.
    `tokens` may be a list/tuple or a whitespace-separated string. Returns safe HTML.
    """
    if not text:
        return ''
    if not tokens:
        return escape(text)

    # normalize tokens to list of non-empty strings
    if isinstance(tokens, str):
        toks = [t for t in re.split(r'\s+', tokens) if t]
    else:
        toks = [t for t in tokens if t]
    if not toks:
        return escape(text)

    # sort by length desc so longer tokens are matched first (avoid partial matches)
    toks = sorted(set(toks), key=lambda s: -len(s))
    pattern = re.compile('|'.join(re.escape(t) for t in toks), re.IGNORECASE)

    parts = []
    last = 0
    for m in pattern.finditer(text):
        # append escaped chunk before match
        parts.append(escape(text[last:m.start()]))
        # append escaped match wrapped in mark
        parts.append(f'<mark class="search-hit">{escape(text[m.start():m.end()])}</mark>')
        last = m.end()
    parts.append(escape(text[last:]))
    return mark_safe(''.join(parts))