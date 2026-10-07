"""Regenerate docs/index.html and the docs/tags/with-<companion>/ folders.

    python tools/build.py

Inputs (all under docs/tags/):
    manifest.json                  the options (number, name, description, file or levels)
    plain/*.html                   each tag on its own
    companions/companions.json     the companion images (id, name, w, h) ...
    companions/<id>.html           ... and their <img> fragments (made by tools/art/make_companion.py)

Outputs:
    docs/index.html                the gallery page; embeds every tag and companion so it also works from file://
    docs/tags/with-<id>/*.html     every plain tag with companion <id> appended on the right (one folder per companion;
                                   folders for companions that no longer exist are removed)
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGS_DIR = os.path.join(ROOT, 'docs', 'tags')
PLAIN_DIR = os.path.join(TAGS_DIR, 'plain')
COMP_DIR = os.path.join(TAGS_DIR, 'companions')


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def js(value):
    # '</' would end the inline <script> early
    return json.dumps(value, ensure_ascii=False).replace('</', '<\\/')


def with_companion(tag_html, c):
    """Must match withComp() in tools/index.template.html."""
    return ('<div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; max-width: calc(100vw - 56px)">' + tag_html +
            f'<span style="position: relative; display: inline-block; width: {c["w"]}px; height: {c["h"]}px">' + c['html'] + '</span></div>')


manifest = sorted(json.loads(read(os.path.join(TAGS_DIR, 'manifest.json'))), key=lambda m: m['n'])
tags = []
for m in manifest:
    t = {'n': m['n'], 'label': f"{m['n']}. {m['name']}" if m['n'] else m['name'], 'desc': m['desc']}
    if 'levels' in m:      # scene tags: with and without the heart pair
        t['levels'] = {lvl: read(os.path.join(PLAIN_DIR, f)) for lvl, f in m['levels'].items()}
    else:
        t['html'] = read(os.path.join(PLAIN_DIR, m['file']))
    tags.append(t)

companions = json.loads(read(os.path.join(COMP_DIR, 'companions.json')))
for c in companions:
    c['html'] = read(os.path.join(COMP_DIR, c['file']))

# with-<id>/ folders
wanted = {f'with-{c["id"]}' for c in companions}
for d in os.listdir(TAGS_DIR):
    if d.startswith('with-') and d not in wanted and os.path.isdir(os.path.join(TAGS_DIR, d)):
        shutil.rmtree(os.path.join(TAGS_DIR, d))
for c in companions:
    out = os.path.join(TAGS_DIR, f'with-{c["id"]}')
    os.makedirs(out, exist_ok=True)
    plain_files = sorted(os.listdir(PLAIN_DIR))
    for f in plain_files:
        write(os.path.join(out, f), with_companion(read(os.path.join(PLAIN_DIR, f)), c))
    for f in os.listdir(out):                       # drop files for tags that were removed
        if f not in plain_files:
            os.remove(os.path.join(out, f))

page = (read(os.path.join(ROOT, 'tools', 'index.template.html'))
        .replace('@@TAGS@@', js(tags))
        .replace('@@COMPS@@', js([{k: c[k] for k in ('id', 'name', 'w', 'h', 'html')} for c in companions])))
write(os.path.join(ROOT, 'docs', 'index.html'), page)
print(f'wrote docs/index.html ({len(page):,} chars): {len(tags)} tags, {len(companions)} companions ({", ".join(c["id"] for c in companions)})')
