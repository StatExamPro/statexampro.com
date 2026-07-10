#!/usr/bin/env python3
"""Pre-push verification for statexampro.com. Run from anywhere:
  python3 tools/check_site.py
Exits non-zero if anything fails. Checks, in order:
  parity of data-en/data-fr, no arrows, every internal href/src resolves,
  tag balance, inline JS parses (node --check), JSON-LD is valid JSON,
  every CSS class used is defined (site.css or the page's <style>),
  visible text matches the data-attr of the page's language (the "flip"),
  footers byte-identical within each language, sitenav on internal pages,
  FR tree never links the EN tree or the US store, no legacy i18n tokens,
  formulas localized on FR, sitemap matches the files on disk,
  theme script lives only in site.js, and `build_fr.py --check` is a no-op.
"""
import re, os, sys, glob, json, hashlib, shutil, tempfile, subprocess, posixpath

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fail = []

def report(msg):
    fail.append(msg)

files = sorted(glob.glob('**/*.html', recursive=True))
LANDINGS = {'index.html', 'fr/index.html'}
LEGACY = ('applyLang', 'navigator.language', 'segEn', 'sxp-lang', 'data-en=""')
ELEM = re.compile(r'<(\w+)((?:[^>"]|"[^"]*")*?)\sdata-(en|fr)="([^"]*)"\s+data-(en|fr)="([^"]*)"((?:[^>"]|"[^"]*")*?)>')

site_css = open('site.css', encoding='utf-8').read()
have_node = shutil.which('node') is not None
if not have_node:
    print('note: node not found, skipping JS syntax checks')

en_footers, fr_footers = set(), set()

for f in files:
    s = open(f, encoding='utf-8').read()
    lang = 'fr' if f.startswith('fr/') else 'en'
    d = posixpath.dirname(f)

    if s.count('data-en=') != s.count('data-fr='):
        report(f'{f}: data-en count != data-fr count')
    if re.search(r'→|&rarr;|&#8594;', s):
        report(f'{f}: arrow character (rendered ugly, banned)')
    for tok in LEGACY:
        if tok in s:
            report(f'{f}: legacy token {tok!r}')

    # refs resolve
    for h in re.findall(r'(?:href|src)="([^"#]+)"', s):
        if h.startswith(('http', 'mailto:', '//', 'data:')):
            continue
        p = h.lstrip('/') if h.startswith('/') else posixpath.normpath(posixpath.join(d, h))
        if p == '':
            p = 'index.html'
        elif p.endswith('/'):
            p += 'index.html'
        elif not re.search(r'\.\w+$', p):
            p += '/index.html'
        if not os.path.exists(p):
            report(f'{f}: broken ref {h}')

    # tag balance (scripts excluded: JS builds markup from strings)
    body = re.sub(r'<script[\s\S]*?</script>', '', s)
    for tag in ('div', 'section', 'footer', 'article', 'span', 'a', 'p', 'nav', 'main', 'ul', 'li', 'table'):
        if len(re.findall(r'<%s[\s>]' % tag, body)) != len(re.findall(r'</%s>' % tag, body)):
            report(f'{f}: <{tag}> open/close imbalance')

    # inline JS parses
    if have_node:
        for i, m in enumerate(re.finditer(r'<script>([\s\S]*?)</script>', s)):
            with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as t:
                t.write(m.group(1)); tn = t.name
            r = subprocess.run(['node', '--check', tn], capture_output=True, text=True)
            os.unlink(tn)
            if r.returncode != 0:
                report(f'{f} inline script #{i}: JS syntax error')

    # JSON-LD valid
    for m in re.finditer(r'<script type="application/ld\+json">([\s\S]*?)</script>', s):
        try:
            json.loads(m.group(1))
        except Exception as e:
            report(f'{f}: invalid JSON-LD ({e})')

    # CSS coverage
    local_css = ' '.join(re.findall(r'<style>([\s\S]*?)</style>', s))
    for cl in set(sum((c.split() for c in re.findall(r'class="([^"]+)"', body)), [])):
        if ('.' + cl) not in site_css and ('.' + cl) not in local_css:
            report(f'{f}: class .{cl} not defined in site.css or local style')

    # visible text == data-attr of this page's language
    for m in ELEM.finditer(s):
        tag = m.group(1)
        attrs = {m.group(3): m.group(4), m.group(5): m.group(6)}
        if set(attrs) != {'en', 'fr'}:
            continue
        rest = s[m.end():]
        close = rest.find(f'</{tag}>')
        if close == -1 or f'<{tag}' in rest[:close]:
            continue
        if rest[:close].strip() != attrs[lang].strip():
            report(f'{f}: visible text != data-{lang} on <{tag}>: {attrs[lang][:50]!r}')

    # footer pools
    m = re.search(r'<footer>[\s\S]*?</footer>', s)
    if m:
        (fr_footers if lang == 'fr' else en_footers).add(hashlib.md5(m.group(0).encode()).hexdigest())
    else:
        report(f'{f}: no footer')

    # sitenav on internal pages only
    has_nav = '<nav class="sitenav">' in s
    if f in LANDINGS and has_nav:
        report(f'{f}: sitenav on landing (should not be there)')
    if f not in LANDINGS and not has_nav:
        report(f'{f}: sitenav missing')

    # FR-tree language hygiene
    if lang == 'fr':
        s_noseg = re.sub(r'<div class="seg"[\s\S]*?</div>', '', s)
        for h in re.findall(r'href="(/[^"#]*)"', s_noseg):
            if not h.startswith('/fr/') and h != '/privacy.html':
                report(f'{f}: FR page links into EN tree: {h}')
        if re.search(r'(?<=[ >])href="https://apps\.apple\.com/us/', s):
            report(f'{f}: bare App Store link points to /us/')
        if re.search(r'\\text\{PPV\}|\\text\{NPV\}|\\text\{sick\}|\\text\{healthy\}', s):
            report(f'{f}: unlocalized formula token')

if len(en_footers) > 1 or len(fr_footers) > 1:
    report(f'footers diverged: {len(en_footers)} EN variants, {len(fr_footers)} FR variants')

# theme script single-sourced
for f in files:
    if 'function currentTheme' in open(f, encoding='utf-8').read():
        report(f'{f}: theme functions inline (belong in site.js only)')
if have_node and subprocess.run(['node', '--check', 'site.js'], capture_output=True).returncode != 0:
    report('site.js: JS syntax error')

# sitemap <-> disk
locs = set(re.findall(r'<loc>([^<]+)</loc>', open('sitemap.xml', encoding='utf-8').read()))
disk = {'https://statexampro.com/privacy.html'} | \
       {'https://statexampro.com/' + f.replace('index.html', '') for f in files if f != 'privacy.html'}
for missing in sorted(disk - locs):
    report(f'sitemap: missing {missing}')
for extra in sorted(locs - disk):
    report(f'sitemap: lists non-existent {extra}')

# FR tree is exactly what build_fr.py produces
r = subprocess.run([sys.executable, 'tools/build_fr.py', '--check'], capture_output=True, text=True)
if '0 page(s) differ' not in r.stdout:
    report('fr/ tree is not what build_fr.py generates - run: python3 tools/build_fr.py\n'
           + '\n'.join(l for l in r.stdout.splitlines() if l.startswith('  ~')))

if fail:
    print(f'FAIL: {len(fail)} problem(s)')
    for x in fail:
        print(' -', x)
    sys.exit(1)
print(f'OK: {len(files)} pages clean (refs, parity, flip, JS, JSON-LD, CSS, footers, sitenav, sitemap, fr-build)')
