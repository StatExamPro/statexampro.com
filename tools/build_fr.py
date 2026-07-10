#!/usr/bin/env python3
"""Build the /fr/ tree from the EN tree. The EN pages are the single source of
truth: every translatable element carries data-en/data-fr, and this script
flips the visible text to data-fr plus rewrites the language mechanics
(canonical/hreflang, /fr/ links, asset depths, store links, LANG, formulas).
Head metadata (title/description/og) and JSON-LD live in tools/fr-meta.json.

Usage, from the repo root (v260709/):
  python3 tools/build_fr.py --check   # dry run: show diff vs current fr/, write nothing
  python3 tools/build_fr.py           # regenerate fr/ in place

Never edit files under fr/ by hand - they are build output.
"""
import re, os, sys, glob, json, difflib, posixpath

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
META = json.load(open('tools/fr-meta.json', encoding='utf-8'))
CHECK = '--check' in sys.argv

SEP = '<span style="opacity:.3">|</span>'
FOOTER_FR = f'''<footer>
 <p>&copy; 2026 Stat Exam Pro</p>
 <p><a href="/fr/">Accueil</a>{SEP}<a href="/fr/ppv-calculator/">Simulateur VPP/VPN</a>{SEP}<a href="/fr/nnt-calculator/">Simulateur NNT</a>{SEP}<a href="/fr/roc-curve/">Simulateur ROC</a>{SEP}<a href="/fr/lessons/roc-auc/">Cours ROC et AUC</a></p>
 <p><a href="/fr/fails/">Stat Fails</a> : <a href="/fr/fails/hiv-false-positives/">Les conseillers sûrs à 100 %</a>{SEP}<a href="/fr/fails/the-1995-pill-scare/">La panique de la pilule de 1995</a>{SEP}<a href="/fr/fails/epic-sepsis-model/">L'IA de sepsis</a></p>
 <p><a href="/fr/studies/">Études et jeux de données connus</a>{SEP}<a href="/privacy.html">Politique de confidentialité</a>{SEP}<a href="mailto:support@statexampro.com">Support</a></p>
</footer>'''

SITENAV_LABELS = {'PPV/NPV': 'VPP/VPN', 'Lesson': 'Cours', 'Studies': 'Études'}
FORMULA_MAP = [('\\text{PPV}', '\\text{VPP}'), ('\\text{NPV}', '\\text{VPN}'),
               ('\\text{score}_{\\text{sick}}', '\\text{score}_{\\text{malade}}'),
               ('\\text{score}_{\\text{healthy}}', '\\text{score}_{\\text{sain}}')]

ELEM = re.compile(r'<(\w+)((?:[^>"]|"[^"]*")*?)\sdata-(en|fr)="([^"]*)"\s+data-(en|fr)="([^"]*)"((?:[^>"]|"[^"]*")*?)>')

def flip_to_fr(s, path):
    """Visible content of every paired element := data-fr."""
    edits = []
    for m in ELEM.finditer(s):
        tag = m.group(1)
        attrs = {m.group(3): m.group(4), m.group(5): m.group(6)}
        if set(attrs) != {'en', 'fr'}:
            continue
        fr = attrs['fr']
        rest = s[m.end():]
        close = rest.find(f'</{tag}>')
        if close == -1:
            continue
        if f'<{tag}' in rest[:close]:
            sys.exit(f"{path}: nested <{tag}> inside paired element - split it or restructure")
        if 'href="/' in fr:
            sys.exit(f"{path}: data-fr contains a root link; link rewriting happens before the flip")
        edits.append((m.end(), m.end() + close, fr))
    for a, b, fr in reversed(edits):
        s = s[:a] + fr + s[b:]
    return s

def rel_refs(s, en_dir, fr_dir):
    """Re-resolve relative href/src for the deeper FR directory."""
    def fix(m):
        attr, val = m.group(1), m.group(2)
        if val.startswith(('http', '//', '/', 'mailto:', '#', 'data:')):
            return m.group(0)
        target = posixpath.normpath(posixpath.join(en_dir, val)) if en_dir else val
        return f'{attr}="{posixpath.relpath(target, fr_dir)}"'
    return re.sub(r'\b(href|src)="([^"]*)"', fix, s)

def build(en_path):
    fr_path = 'fr/' + en_path
    en_dir = posixpath.dirname(en_path)
    fr_dir = 'fr/' + en_dir if en_dir else 'fr'
    en_url = '/' + (en_dir + '/' if en_dir else '')
    fr_url = '/fr' + en_url
    meta = META[en_path]
    s = open(en_path, encoding='utf-8').read()

    # head
    s = must(s, '<html lang="en">', '<html lang="fr">', en_path)
    s = re.sub(r'<title>[^<]*</title>', '<title>' + meta['title'] + '</title>', s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', r'\g<1>' + meta['description'].replace('\\', '\\\\') + r'\g<2>', s, count=1)
    for key, prop in (('og:title', 'og:title'), ('og:description', 'og:description')):
        if key in meta:
            s = re.sub(r'(property="%s" content=")[^"]*(")' % prop, r'\g<1>' + meta[key].replace('\\', '\\\\') + r'\g<2>', s, count=1)
    s = must(s, f'rel="canonical" href="https://statexampro.com{en_url}"',
                f'rel="canonical" href="https://statexampro.com{fr_url}"', en_path)
    s = must(s, f'property="og:url" content="https://statexampro.com{en_url}"',
                f'property="og:url" content="https://statexampro.com{fr_url}"', en_path)
    s = must(s, 'property="og:locale" content="en_US"', 'property="og:locale" content="fr_FR"', en_path)
    s = must(s, 'property="og:locale:alternate" content="fr_FR"', 'property="og:locale:alternate" content="en_US"', en_path)

    # JSON-LD blocks: verbatim FR versions from fr-meta.json
    blocks = re.findall(r'<script type="application/ld\+json">[\s\S]*?</script>', s)
    if len(blocks) != len(meta['jsonld']):
        sys.exit(f"{en_path}: {len(blocks)} JSON-LD blocks vs {len(meta['jsonld'])} in fr-meta.json - update the json")
    for old, new in zip(blocks, meta['jsonld']):
        s = s.replace(old, '<script type="application/ld+json">' + new + '</script>', 1)

    # links & assets
    s = rel_refs(s, en_dir, fr_dir)
    s = re.sub(r'href="/(?!fr/|privacy\.html)', 'href="/fr/', s)          # root-relative -> /fr/
    s = re.sub(r'href="/fr/"(?=[^>]*hreflang="fr")', 'href="/fr/"', s)   # no-op guard, kept for clarity
    seg = re.compile(r'<div class="seg" role="group" aria-label="Language">[\s\S]*?</div>')
    if not seg.search(s):
        sys.exit(f"{en_path}: language switcher not found")
    s = seg.sub(f'<div class="seg" role="group" aria-label="Language"><a href="{en_url}" hreflang="en">EN</a><span class="active">FR</span></div>', s, count=1)
    s = re.sub(r'(?<=[ >])href="https://apps\.apple\.com/us/', 'href="https://apps.apple.com/fr/', s)

    # chrome: footer template, sitenav labels
    if '<footer>' in s:
        s = re.sub(r'<footer>[\s\S]*?</footer>', FOOTER_FR, s, count=1)
    nav = re.search(r'<nav class="sitenav">[\s\S]*?</nav>', s)
    if nav:
        block = nav.group(0)
        for en_l, fr_l in SITENAV_LABELS.items():
            block = block.replace('>' + en_l + '</a>', '>' + fr_l + '</a>')
        s = s[:nav.start()] + block + s[nav.end():]

    # page mechanics
    s = s.replace("var LANG = 'en'", "var LANG = 'fr'").replace("var LANG='en'", "var LANG='fr'")
    for a, b in FORMULA_MAP:
        s = s.replace(a, b)

    # images with language variants
    def img_fix(m):
        tag = m.group(0)
        src_fr = re.search(r'data-src-fr="([^"]*)"', tag)
        if src_fr:
            target = posixpath.normpath(posixpath.join(en_dir, src_fr.group(1))) if en_dir else src_fr.group(1)
            tag = re.sub(r'src="[^"]*"', 'src="%s"' % posixpath.relpath(target, fr_dir), tag, count=1)
        alt_fr = re.search(r'data-alt-fr="([^"]*)"', tag)
        if alt_fr:
            tag = re.sub(r'(?<=\s)alt="[^"]*"', 'alt="%s"' % alt_fr.group(1), tag, count=1)
        if 'fig1-en.png' in tag:
            tag = tag.replace('fig1-en.png', 'fig1-fr.png')
            if 'fig1-alt' in meta:
                tag = re.sub(r'(?<=\s)alt="[^"]*"', 'alt="%s"' % meta['fig1-alt'], tag, count=1)
        return tag
    s = re.sub(r'<img[^>]*>', img_fix, s)

    # the content itself
    s = flip_to_fr(s, en_path)

    # self-checks
    for pat, msg in [(r'(?<=[ >])href="https://apps\.apple\.com/us/', 'bare US store link'),
                     (r'\\text\{PPV\}|\\text\{NPV\}', 'unlocalized formula token'),
                     (r'<html lang="en">', 'lang not flipped')]:
        if re.search(pat, s):
            sys.exit(f"{fr_path}: check failed: {msg}")
    for m in re.finditer(r'\b(href|src)="([^"#]+)"', s):
        v = m.group(2)
        if v.startswith(('http', '//', 'mailto:', 'data:')):
            continue
        p = v.lstrip('/') if v.startswith('/') else posixpath.normpath(posixpath.join(fr_dir, v))
        if p == '':
            p = 'index.html'
        elif p.endswith('/'):
            p += 'index.html'
        elif not re.search(r'\.\w+$', p):
            p += '/index.html'
        if not os.path.exists(p):
            sys.exit(f"{fr_path}: broken ref {v}")
    return fr_path, s

def must(s, old, new, path):
    if s.count(old) != 1:
        sys.exit(f"{path}: expected exactly one {old!r}")
    return s.replace(old, new)

pages = sorted(p for p in glob.glob('**/index.html', recursive=True) if not p.startswith('fr/'))
changed = 0
for en_path in pages:
    if en_path not in META:
        sys.exit(f"{en_path}: no entry in tools/fr-meta.json - add title/description/og/jsonld for the FR version")
    fr_path, out = build(en_path)
    cur = open(fr_path, encoding='utf-8').read() if os.path.exists(fr_path) else ''
    if out == cur:
        print(f"  = {fr_path}")
        continue
    changed += 1
    if CHECK:
        diff = list(difflib.unified_diff(cur.splitlines(), out.splitlines(),
                                         fr_path + ' (current)', fr_path + ' (generated)', lineterm=''))
        print(f"  ~ {fr_path}: {sum(1 for l in diff if l.startswith(('+', '-')))} diff lines")
        for l in diff[:400]:
            print('   ', l)
    else:
        os.makedirs(os.path.dirname(fr_path), exist_ok=True)
        open(fr_path, 'w', encoding='utf-8').write(out)
        print(f"  W {fr_path}")
print(('check: ' if CHECK else 'written: ') + f'{changed} page(s) differ, {len(pages) - changed} identical')
