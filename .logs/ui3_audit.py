#!/usr/bin/env python3
"""Static phone-layout guardrails; not a browser/computed-layout test.

Run: .venv/bin/python .logs/ui3_audit.py
Checks source CSS/templates, allowing bounded widths and widths inside scrollers.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'src/imocha_raven/app'
issues = []


def issue(file, message):
    issues.append(f'{file}: {message}')


def rules(text, contexts=()):
    """Read nested media rules without confusing keyframe steps with selectors."""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    pos = 0
    while (opening := text.find('{', pos)) != -1:
        header = text[pos:opening].strip()
        depth, closing = 1, opening + 1
        while closing < len(text) and depth:
            depth += (text[closing] == '{') - (text[closing] == '}')
            closing += 1
        if depth:
            issue('style.css', 'unbalanced CSS braces')
            return
        body = text[opening + 1:closing - 1]
        if header.startswith('@media'):
            yield from rules(body, contexts + (header,))
        elif not header.startswith('@'):
            yield header, dict(re.findall(r'([\w-]+)\s*:\s*([^;]+)', body)), contexts
        pos = closing


def pixels(value):
    match = re.fullmatch(r'([\d.]+)(px|rem|em)(?:\s*!important)?', value.strip())
    return float(match[1]) * (16 if match[2] != 'px' else 1) if match else None


css = (APP / 'static/style.css').read_text()
parsed = list(rules(css))
for selector, declarations, contexts in parsed:
    for prop in ('width', 'min-width'):
        width = pixels(declarations.get(prop, ''))
        if width and width > 360:
            # The table's intentional width is contained by its own scroll viewport.
            if '.table-scroll' in selector and ('table' in selector or 'engine-table' in selector):
                continue
            issue('style.css', f'{selector}: fixed {prop} {width:g}px > 360px')
    if re.search(r'\b(input|textarea|select)\b', selector):
        size = pixels(declarations.get('font-size', ''))
        if size and size < 16:
            issue('style.css', f'{selector}: control font {size:g}px < 16px')

if not any(all(t in selector.split(',') for t in ('input', 'textarea', 'select'))
           and pixels(declarations.get('font-size', '')) >= 16
           for selector, declarations, _ in parsed
           if pixels(declarations.get('font-size', '')) is not None):
    issue('style.css', 'missing shared 16px control font floor')
if not any('.table-scroll' == selector and declarations.get('overflow-x') == 'auto'
           for selector, declarations, _ in parsed):
    issue('style.css', 'missing table overflow-x:auto')
if 'background-attachment:local,local,scroll,scroll' not in css:
    issue('style.css', 'missing table edge fades')


class TemplateAudit(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, filename):
        super().__init__()
        self.filename, self.stack = filename, []
        self.tables = self.controls = self.svgs = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table':
            self.tables += 1
            if not any('table-scroll' in a.get('class', '').split() for _, a in self.stack):
                issue(self.filename, 'table missing .table-scroll ancestor')
        if tag == 'svg':
            self.svgs += 1
            if 'viewbox' not in attrs:
                issue(self.filename, 'inline SVG missing viewBox')
        if tag in {'input', 'textarea', 'select'}:
            self.controls += 1
        for prop, value in re.findall(r'(font-size|(?:min-)?width)\s*:\s*([^;]+)', attrs.get('style', '')):
            number = pixels(value)
            if number is not None and prop == 'font-size' and tag in {'input', 'textarea', 'select'} and number < 16:
                issue(self.filename, f'inline {tag} font {number:g}px < 16px')
            if number is not None and prop != 'font-size' and number > 360:
                issue(self.filename, f'inline fixed {prop} {number:g}px > 360px')
        # Intrinsic image/SVG dimensions are safe only with their responsive CSS.
        if tag in {'img', 'svg'} and attrs.get('width', '').isdigit() and int(attrs['width']) > 360:
            if not (tag == 'img' and 'img{max-width:100%;height:auto}' in css) and tag != 'svg':
                issue(self.filename, 'unbounded intrinsic image width')
        if tag not in self.VOID:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)


totals = [0, 0, 0]
files = sorted((APP / 'templates').glob('*.html'))
for path in files:
    parser = TemplateAudit(path.name)
    source = re.sub(r'{[%{].*?[%}]}', 'fixture', path.read_text(), flags=re.S)
    parser.feed(source)
    totals = [a + b for a, b in zip(totals, (parser.tables, parser.controls, parser.svgs))]
print(f'Audited {len(files)} templates and {len(parsed)} CSS rules: {totals[0]} tables, {totals[1]} controls, {totals[2]} SVG definitions.')
for message in issues:
    print('FAIL:', message)
print(f'{"FAIL" if issues else "PASS"}: {len(issues)} static findings. Runtime layout/keyboard behavior still requires device testing.')
if __name__ == '__main__':
    sys.exit(bool(issues))
