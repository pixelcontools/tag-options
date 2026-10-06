"""Regenerate docs/index.html from docs/tags/ (manifest.json, plain/*.html, roll.html).

    python tools/build.py

The page embeds every tag, so it also works when opened straight from disk (file://).
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGS_DIR = os.path.join(ROOT, 'docs', 'tags')


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def js(value):
    # '</' would end the inline <script> early
    return json.dumps(value, ensure_ascii=False).replace('</', '<\\/')


manifest = json.loads(read(os.path.join(TAGS_DIR, 'manifest.json')))
tags = [{'n': m['n'], 'label': f"{m['n']}. {m['name']}" if m['n'] else m['name'], 'desc': m['desc'],
         'html': read(os.path.join(TAGS_DIR, 'plain', m['file']))} for m in manifest]
page = (read(os.path.join(ROOT, 'tools', 'index.template.html'))
        .replace('@@TAGS@@', js(tags))
        .replace('@@ROLL@@', js(read(os.path.join(TAGS_DIR, 'roll.html')))))
with open(os.path.join(ROOT, 'docs', 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(page)
print('wrote docs/index.html', len(page), 'chars,', len(tags), 'tags')
