#!/usr/bin/env python3
"""
שלבי הקוד של המדריך.

stages/NN/ מחזיק רק את הקבצים שהשתנו בשלב NN (תוכן מלא), נתיבים יחסית ל-src/.
קובץ stages/NN/DELETE מונה קבצים שנמחקים בשלב הזה.
מצב הקוד בסוף שלב N = שלב 01 ועליו כל השלבים עד N, לפי הסדר.

  stages.py verify [N...]   בונה כל שלב כפרויקט מלא בתיקייה זמנית ומריץ Gradle (קומפילציה, ובדיקות אם יש)
  stages.py sync            כותב את השלב האחרון אל app/app/src (הפרויקט להורדה)
  stages.py render IN OUT   מרחיב את הסימונים ב-sections.html לכרטיסי קוד:
      {{ADD:NN|path|כותרת}}   הקובץ בשלב NN, מה שנוסף/השתנה מודגש, קוד שלא השתנה מקופל ל-⋮
      {{FULL:NN|path|כותרת}}  הקובץ כולו כפי שהוא בסוף שלב NN (פתוח, עם העתקה)
      {{SNAP:NN|path,path}}   "הקוד המלא בסוף השלב": כרטיסים סגורים עם העתקה
"""
import difflib
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

UNIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGES = os.path.join(UNIT, 'stages')
APP = os.path.join(UNIT, 'app')
SRC = os.path.join(APP, 'app', 'src')
CONTEXT = 3

# קבצים שאנדרואיד סטודיו יוצר ואף שלב לא נוגע בהם: נלקחים מהפרויקט הסופי כמו שהם
STATIC = re.compile(r'^main/res/(mipmap-[^/]+/.*|drawable/ic_launcher_.*)$')


def stage_ids():
    return sorted(d for d in os.listdir(STAGES) if re.fullmatch(r'\d\d', d))


def walk(root):
    out = {}
    for dp, _, files in os.walk(root):
        for f in files:
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, root).replace(os.sep, '/')
            if rel != 'DELETE':
                out[rel] = full
    return out


def assemble(n):
    """{path: content} בסוף שלב n."""
    tree = {}
    for sid in stage_ids():
        if int(sid) > int(n):
            break
        d = os.path.join(STAGES, sid)
        dele = os.path.join(d, 'DELETE')
        if os.path.exists(dele):
            for line in open(dele, encoding='utf-8'):
                if line.strip():
                    tree.pop(line.strip(), None)
        for rel, full in walk(d).items():
            tree[rel] = open(full, encoding='utf-8').read()
    return tree


def static_files():
    return {rel: full for rel, full in walk(SRC).items() if STATIC.match(rel)}


# ---------------------------------------------------------------- verify / sync

def verify(ids):
    ok = True
    for sid in ids:
        tmp = tempfile.mkdtemp(prefix='stage%s-' % sid)
        proj = os.path.join(tmp, 'proj')
        shutil.copytree(APP, proj, ignore=shutil.ignore_patterns('build', '.gradle', 'src'))
        src = os.path.join(proj, 'app', 'src')
        for rel, full in static_files().items():
            os.makedirs(os.path.dirname(os.path.join(src, rel)), exist_ok=True)
            shutil.copy(full, os.path.join(src, rel))
        tree = assemble(sid)
        for rel, text in tree.items():
            p = os.path.join(src, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(text)
        tasks = ['assembleDebug']
        if any(r.startswith('test/') for r in tree):
            tasks.append('testDebugUnitTest')
        r = subprocess.run(['./gradlew', '--offline', '-q'] + tasks, cwd=proj,
                           capture_output=True, text=True)
        print('stage %s: %s' % (sid, 'OK' if r.returncode == 0 else 'FAILED'), ' '.join(tasks))
        if r.returncode != 0:
            ok = False
            print((r.stdout + r.stderr)[-3000:])
        shutil.rmtree(tmp, ignore_errors=True)
    return ok


def sync():
    last = stage_ids()[-1]
    tree = assemble(last)
    for rel, full in walk(SRC).items():
        if not STATIC.match(rel) and rel not in tree:
            os.remove(full)
    for rel, text in tree.items():
        p = os.path.join(SRC, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(text)
    for dp, dirs, files in os.walk(SRC, topdown=False):
        if not dirs and not files:
            os.rmdir(dp)
    print('app/ synced to stage', last)


# ---------------------------------------------------------------- render

def nice(path):
    p = re.sub(r'^main/java/com/example/hebrewwordle/', '', path)
    p = re.sub(r'^main/', '', p)
    p = re.sub(r'^test/java/com/example/hebrewwordle/', 'test/.../', p)
    return p


def card(title, body, open_=True, copy=True, extra=''):
    btns = '<button class="btn btn-toggle">%s</button>' % ('הסתר קוד ˄' if open_ else 'הצג קוד ˅')
    if copy:
        btns += '<button class="btn btn-copy">העתק קוד 📋</button>'
    return ('<div class="codecard%s">\n  <div class="codecard-head">\n'
            '    <span class="codecard-file">%s</span>\n'
            '    <span class="codecard-btns">%s</span>\n  </div>\n'
            '<pre%s><code>%s</code></pre>\n</div>' % (extra, title, btns, ' class="open"' if open_ else '', body))


def ln(cls, text):
    return '<span class="ln %s">%s</span>' % (cls, html.escape(text) or ' ')


def diff_body(old, new):
    a, b = old.splitlines(), new.splitlines()
    ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    keep = [False] * len(b)            # אילו שורות של הקובץ החדש מוצגות
    changed_at = {}                    # אינדקס בקובץ החדש -> שורות שנמחקו לפניו
    for tag, i1, i2, j1, j2 in ops:
        if tag == 'equal':
            continue
        for j in range(max(0, j1 - CONTEXT), min(len(b), j2 + CONTEXT)):
            keep[j] = True
        if tag in ('delete', 'replace'):
            changed_at.setdefault(j1, []).extend(a[i1:i2])
            if j1 < len(b):
                keep[j1] = True
            for j in range(max(0, j1 - CONTEXT), j1):
                keep[j] = True
    added = set()
    for tag, i1, i2, j1, j2 in ops:
        if tag in ('insert', 'replace'):
            added.update(range(j1, j2))
    out, gap = [], False
    for j in range(len(b) + 1):
        for d in changed_at.get(j, []):
            out.append(ln('del', d))
        if j == len(b):
            break
        if keep[j]:
            if gap:
                out.append(ln('gap', '    ⋮'))
                gap = False
            out.append(ln('add' if j in added else 'ctx', b[j]))
        else:
            gap = True
    if gap:
        out.append(ln('gap', '    ⋮'))
    return '\n'.join(out)


def render(src, dst):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import diagrams
    text = diagrams.expand(open(src, encoding='utf-8').read())

    def add(m):
        sid, path, title = m.group(1), m.group(2), m.group(3)
        new = assemble(sid).get(path)
        if new is None:
            sys.exit('ADD: %s not in stage %s' % (path, sid))
        prev = assemble('%02d' % (int(sid) - 1)).get(path)
        if prev is None or prev == '':
            body = new.rstrip('\n')
            return card(title + ' <small>(קובץ חדש)</small>', html.escape(body),
                        open_=body.count('\n') < 45)
        if prev == new:
            sys.exit('ADD: %s did not change in stage %s' % (path, sid))
        return card(title + ' <small>(מה מוסיפים)</small>', diff_body(prev, new), copy=False, extra=' diff')

    def full(m):
        sid, path, title = m.group(1), m.group(2), m.group(3)
        body = assemble(sid).get(path)
        if body is None:
            sys.exit('FULL: %s not in stage %s' % (path, sid))
        return card(title, html.escape(body.rstrip('\n')))

    def snap(m):
        sid, paths = m.group(1), m.group(2).split(',')
        tree = assemble(sid)
        cards = []
        for p in paths:
            if p not in tree:
                sys.exit('SNAP: %s not in stage %s' % (p, sid))
            cards.append(card(nice(p) + ' – כפי שהוא בסוף שלב %d' % int(sid),
                              html.escape(tree[p].rstrip('\n')), open_=False))
        return ('<div class="snapshot">\n  <h3>📄 הקוד המלא בסוף השלב – השוו לשלכם</h3>\n'
                + '\n'.join(cards) + '\n</div>')

    text = re.sub(r'\{\{ADD:(\d\d)\|([^|}]+)\|([^}]+)\}\}', add, text)
    text = re.sub(r'\{\{FULL:(\d\d)\|([^|}]+)\|([^}]+)\}\}', full, text)
    text = re.sub(r'\{\{SNAP:(\d\d)\|([^}]+)\}\}', snap, text)
    open(dst, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'verify':
        sys.exit(0 if verify(sys.argv[2:] or stage_ids()) else 1)
    elif cmd == 'sync':
        sync()
    elif cmd == 'render':
        render(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
