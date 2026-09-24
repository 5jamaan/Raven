"""Only a GitHub source revision path is exempt from the generic hex heuristic.

Credential-specific patterns always inspect the original text. Bare hex values,
query strings, lookalike hosts and other URL path components remain screened.
"""
import re

REVISION = re.compile(
    r'(?<![\w/])https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/'
    r'(?:commit|tree|blob)/(?P<sha>[0-9a-fA-F]{40})(?=$|[/#?\s)\]>"\x27])'
)
HEX = r'\b[0-9a-fA-F]{40,64}\b'
ASSIGNMENT = re.compile(
    r'(?:api[_ -]?key|password|parola|access[_ -]?token|refresh[_ -]?token|'
    r'authorization|seed phrase|recovery code|kurtarma kodu)\s*[:=]\s*["\x27]?$', re.I
)


def matches(text, patterns):
    revisions = {m.span('sha') for m in REVISION.finditer(text)
                 if not ASSIGNMENT.search(text[max(0,m.start()-100):m.start()])}
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            if pattern == HEX and match.span() in revisions:
                continue
            yield match


def redact(text, patterns):
    # Reverse-order replacement keeps spans valid, even for overlapping patterns.
    spans = sorted({m.span() for m in matches(text, patterns)})
    merged = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    for start, end in reversed(merged):
        text = text[:start] + '[SIR GİZLENDİ]' + text[end:]
    return text
