"""Build the Sculpture Myra static site from data/sculptures.json.

Usage:  python3 scripts/images.py   # only when photos are added or changed
        python3 scripts/build.py

Generates: index.html, gallery.html, gallery/{stone,wood,other}.html, works/<slug>.html,
resume.html, contact.html, sitemap.xml. Hand-written assets live in css/site.css and js/site.js.
To add a sculpture: add an entry to data/sculptures.json (slug, title, category, material,
dimensions, images = paths to originals under img/), run images.py, then build.py.
"""
import json, os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = 'https://sculpturemyra.com/'
WORKS = json.load(open(os.path.join(ROOT, 'data', 'sculptures.json'), encoding='utf-8'))
IMGS = json.load(open(os.path.join(ROOT, 'data', 'images.json'), encoding='utf-8'))

CATS = [('stone', 'Stone'), ('wood', 'Wood'), ('other', 'Bronze, clay & more')]
CAT_NAME = dict(CATS)
HERO = 'flying'
SELECTED = ['heart-of-the-matter', 'union', 'mr-who', 'seeress', 'lapis', 'bronze-family',
            'emergence', 'whisper', 'luna-landing', 'torso-iii', 'cubic-ii', 'study-in-white']

for w in WORKS:
    w['pics'] = []
    for i in range(1, len(w['images']) + 1):
        name = f"{w['slug']}-{i}.jpg"
        m = IMGS[name]
        w['pics'].append({'name': name, 'w': m['w'], 'h': m['h']})
BY_SLUG = {w['slug']: w for w in WORKS}

e = lambda s: escape(str(s), quote=True)


def img(w, i=0, size='sm', r='', cls='', loading='lazy', sizes=None, alt=None):
    p = w['pics'][i]
    alt = alt if alt is not None else (f"{w['title']}, {w['material']}".rstrip(', ') +
                                        (f" (view {i + 1})" if i else ''))
    srcset = f"{r}img/web/sm/{p['name']} 900w, {r}img/web/lg/{p['name']} 2000w"
    return (f'<img src="{r}img/web/{size}/{p["name"]}" srcset="{srcset}" '
            f'sizes="{sizes or "(max-width: 700px) 100vw, 40vw"}" width="{p["w"]}" height="{p["h"]}" '
            f'alt="{e(alt)}" loading="{loading}" decoding="async"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>')


def details(w):
    rows = [('Material', w['material']), ('Dimensions', w['dimensions']), ('Collection', CAT_NAME[w['category']])]
    return '<dl class="facts">' + ''.join(f'<div><dt>{k}</dt><dd>{e(v)}</dd></div>' for k, v in rows if v) + '</dl>'


def page(r, title, body, *, active='', desc='', og_img=None, canonical='', extra_head='', scripts=''):
    full = 'Myra Lehman, sculptor' if title is None else f'{title} | Myra Lehman, sculptor'
    desc = desc or 'Stone, wood and bronze sculpture by Myra Lehman of Rye, New York. Original works and commissions.'
    og = f'<meta property="og:image" content="{SITE_URL}{og_img}">' if og_img else ''
    nav = ''.join(
        f'<a href="{r}{href}"{" aria-current=page" if active == key else ""}>{label}</a>'
        for key, href, label in [('works', 'gallery.html', 'Works'), ('about', 'resume.html', 'About'),
                                 ('contact', 'contact.html', 'Contact')])
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}{canonical}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
{og}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600&family=Marcellus&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}css/site.css">
<link rel="apple-touch-icon" sizes="180x180" href="{r}apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="{r}favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{r}favicon-16x16.png">
<link rel="manifest" href="{r}site.webmanifest">
<meta name="theme-color" content="#cfcfcb">
{extra_head}
</head>
<body data-root="{r}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <a class="mark" href="{r}index.html">Myra Lehman</a>
  <nav aria-label="Main">{nav}</nav>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot">
  <div class="foot-inner">
    <div>
      <p class="mark">Myra Lehman</p>
      <p>Sculptor, Rye, New York</p>
    </div>
    <ul class="foot-links">
      <li><a href="{r}gallery.html">Works</a></li>
      <li><a href="{r}resume.html">About</a></li>
      <li><a href="{r}contact.html">Contact</a></li>
    </ul>
    <ul class="foot-links">
      <li><a href="mailto:sculpturemyra@optonline.net">sculpturemyra@optonline.net</a></li>
      <li><a href="https://www.facebook.com/myra.lehman" rel="noopener">Facebook</a></li>
      <li><a href="https://www.linkedin.com/in/myra-lehman-8690094/" rel="noopener">LinkedIn</a></li>
    </ul>
  </div>
  <p class="credit"><a href="https://gordonholdingsco.com/">Site by Gordon Enterprises</a></p>
</footer>
<script src="{r}js/site.js" defer></script>
{scripts}
</body>
</html>
'''


def tile(w, r):
    p = w['pics'][0]
    ar = p['w'] / p['h']
    return (f'<a class="tile" href="{r}works/{w["slug"]}.html" data-slug="{w["slug"]}" data-cat="{w["category"]}" '
            f'style="--ar:{ar:.4f}">'
            f'<span class="tile-img">{img(w, r=r, sizes="(max-width: 700px) 100vw, 33vw")}</span>'
            f'<span class="tile-cap"><span class="t">{e(w["title"])}</span>'
            f'<span class="m">{e(w["material"])}</span></span></a>')


def works_json(works):
    return json.dumps([{'slug': w['slug'], 'title': w['title'], 'material': w['material'],
                        'dimensions': w['dimensions'], 'cat': CAT_NAME[w['category']],
                        'pics': [[p['name'], p['w'], p['h']] for p in w['pics']]} for w in works],
                      separators=(',', ':')).replace('</', '<\\/')


def preview_dialog():
    return '''<dialog class="viewer" id="viewer" aria-label="Sculpture preview">
  <div class="viewer-stage">
    <img alt="" id="viewer-img">
    <button class="v-btn v-prev" type="button" data-step="-1" aria-label="Previous sculpture"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
    <button class="v-btn v-next" type="button" data-step="1" aria-label="Next sculpture"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
  </div>
  <aside class="viewer-info">
    <button class="v-close" type="button" aria-label="Close preview"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
    <h2 id="viewer-title"></h2>
    <dl class="facts" id="viewer-facts"></dl>
    <div class="viewer-thumbs" id="viewer-thumbs"></div>
    <p class="viewer-actions"><a class="btn" id="viewer-page" href="#">View this sculpture</a>
    <a class="btn btn-quiet" id="viewer-ask" href="#">Ask about it</a></p>
    <p class="viewer-count" id="viewer-count"></p>
  </aside>
</dialog>'''


def gallery_page(r, preset=''):
    counts = {c: sum(1 for w in WORKS if w['category'] == c) for c, _ in CATS}
    chips = [('', 'All', len(WORKS))] + [(c, n, counts[c]) for c, n in CATS]
    filt = ''.join(
        f'<a class="chip" href="{r}{"gallery/" + c + ".html" if c else "gallery.html"}" data-filter="{c}"'
        f'{" aria-current=true" if c == preset else ""}>{n} <span>{k}</span></a>' for c, n, k in chips)
    tiles = ''.join(tile(w, r) for w in WORKS)
    body = f'''<section class="page-intro wrap">
  <h1>Works</h1>
  <p>Sixty-one sculptures in alabaster, marble, soapstone, hardwoods and bronze. Select any piece for a closer look.</p>
  <nav class="filters" aria-label="Filter by material">{filt}</nav>
</section>
<section class="justified wrap" id="grid" data-preset="{preset}">{tiles}</section>
{preview_dialog()}
<script type="application/json" id="works-data">{works_json(WORKS)}</script>'''
    title = 'Works' if not preset else f'{CAT_NAME[preset]} sculpture'
    canon = 'gallery.html' if not preset else f'gallery/{preset}.html'
    return page(r, title, body, active='works', canonical=canon,
                og_img=f'img/web/lg/{BY_SLUG[HERO]["pics"][0]["name"]}')


def work_page(idx):
    w = WORKS[idx]
    r = '../'
    prev_w, next_w = WORKS[idx - 1], WORKS[(idx + 1) % len(WORKS)]
    thumbs = ''
    if len(w['pics']) > 1:
        thumbs = '<div class="thumbs" role="list">' + ''.join(
            f'<button type="button" role="listitem" class="thumb" data-i="{i}" aria-label="Show view {i + 1}"'
            f'{" aria-current=true" if i == 0 else ""}>'
            f'<img src="{r}img/web/sm/{p["name"]}" alt="" width="{p["w"]}" height="{p["h"]}" loading="lazy"></button>'
            for i, p in enumerate(w['pics'])) + '</div>'
    more = [x for x in WORKS if x['category'] == w['category'] and x['slug'] != w['slug']][:4]
    if len(more) < 4:
        more += [x for x in WORKS if x['category'] != w['category']][:4 - len(more)]
    more_html = ''.join(tile(x, r) for x in more)
    p0 = w['pics'][0]
    body = f'''<article class="work wrap">
  <div class="work-stage">
    <button class="stage-btn" type="button" id="zoom" aria-label="View larger">
      {img(w, 0, 'lg', r, 'stage-img', 'eager', '(max-width: 900px) 100vw, 64vw')}
    </button>
    {thumbs}
  </div>
  <div class="work-info">
    <p class="crumb"><a href="{r}gallery/{w["category"]}.html">{e(CAT_NAME[w["category"]])}</a></p>
    <h1>{e(w["title"])}</h1>
    {details(w)}
    <p class="work-cta"><a class="btn" href="{r}contact.html?piece={w["slug"]}">Ask about this piece</a></p>
    <p class="note">Interested in something similar? Myra also takes commissions.</p>
    <nav class="pager" aria-label="More sculptures">
      <a href="{prev_w["slug"]}.html" rel="prev"><span>Previous</span>{e(prev_w["title"])}</a>
      <a href="{next_w["slug"]}.html" rel="next"><span>Next</span>{e(next_w["title"])}</a>
    </nav>
  </div>
</article>
<section class="more wrap">
  <h2>More {e(CAT_NAME[w["category"]].lower())}</h2>
  <div class="justified">{more_html}</div>
</section>
{preview_dialog()}
<script type="application/json" id="works-data">{works_json([w])}</script>'''
    desc = f'{w["title"]}, a {w["material"].lower() or "sculpture"} sculpture by Myra Lehman' + \
           (f', {w["dimensions"]}.' if w['dimensions'] else '.')
    return page(r, w['title'], body, active='works', desc=desc, canonical=f'works/{w["slug"]}.html',
                og_img=f'img/web/lg/{p0["name"]}')


def index_page():
    r = ''
    h = BY_SLUG[HERO]
    sel = ''.join(tile(BY_SLUG[s], r) for s in SELECTED)
    body = f'''<section class="hero">
  <a class="hero-img" href="works/{h["slug"]}.html" aria-label="{e(h["title"])}, {e(h["material"])}">
    {img(h, 0, 'lg', r, '', 'eager', '100vw', alt=f'{h["title"]}, {h["material"]} sculpture by Myra Lehman')}
  </a>
  <div class="hero-text wrap">
    <h1>Myra Lehman</h1>
    <div class="hero-side">
      <p>Sculpture in stone, wood and bronze, carved in Rye, New York for more than thirty years.</p>
      <p class="hero-caption">Shown: <a href="works/{h["slug"]}.html">{e(h["title"])}</a>, {e(h["material"].lower())}</p>
    </div>
  </div>
</section>
<section class="wrap section">
  <div class="section-head">
    <h2>Selected works</h2>
    <a class="link" href="gallery.html">See all {len(WORKS)} sculptures</a>
  </div>
  <div class="justified" id="grid">{sel}</div>
</section>
<section class="wrap section about-strip">
  <h2>The work</h2>
  <div class="prose">
    <p>Myra follows her ideas toward minimal abstraction, paying close attention to line and to negative space. The pieces are visualizations of mental processes and an expression of the character of each material, whether veined alabaster, Alaska soapstone or a length of black walnut.</p>
    <p>She studied at the Barsanti Studio in Pietrasanta, Italy, and later in Carrara. Her sculptures are in private collections from New York to California and the Netherlands.</p>
    <p class="row-links"><a class="btn" href="contact.html">Commission a piece</a> <a class="link" href="resume.html">Read about Myra</a></p>
  </div>
</section>
{preview_dialog()}
<script type="application/json" id="works-data">{works_json([BY_SLUG[s] for s in SELECTED])}</script>'''
    return page(r, None, body, canonical='', og_img=f'img/web/lg/{h["pics"][0]["name"]}',
                extra_head=f'<link rel="preload" as="image" href="img/web/lg/{h["pics"][0]["name"]}">')


AWARDS = [
    ("First Prize Sculpture", "Mamaroneck Artist's Guild", 2008),
    ("First Prize Sculpture", "Greenwich Art Society", 2007),
    ("First Prize Sculpture", "White Plains Woman's Club", 2007),
    ("First Prize Sculpture", "Art Society of Old Greenwich", 2007),
    ("First Prize Sculpture", "Rye Art Center", 2006),
    ("First Prize Sculpture", "Greenwich Art Society", 2006),
    ("Third Prize Sculpture", "Art Society of Old Greenwich", 2006),
    ("Sculpture Prize", "Bedford Art Show", 2005),
    ("Sculpture Prize", "Bedford Art Show", 2004),
    ("Sculpture Prize", "Bedford Art Show", 2003),
    ("First Prize", "Beaux Arts Finale", 2003),
    ("Sculpture Prize", "Bedford Art Show", 2002),
    ("First Prize", "Bedford Art Show", 2002),
    ("First Prize", "White Plains Woman's Club", 2002),
    ("First Prize", "Mamaroneck Artist's Guild", 2001),
    ("Third Prize", "Art Society of Old Greenwich", 2000),
    ("First Prize", "Art Society of Old Greenwich", 1998),
    ("First Prize", "Beaux Arts Finale", 1997),
    ("First Prize", "Pleasantville Woman's Club", 1995),
    ("Club Award", "Mamaroneck Artist's Guild", 1993),
    ("Second Place", "Salmagundi", 1992),
    ("Second Place", "Art Society of Old Greenwich", 1992),
    ("Second Place", "Mari Galleries, Juried Fine Arts", 1991),
    ("First Prize", "Mamaroneck Woman's Club", 1991),
    ("Argos Award", "Putnam Arts Council", 1990),
    ("First Prize", "Rye Woman's Club, Beaux Arts", 1988),
]


def about_page():
    r = ''
    feat = BY_SLUG['serenity']
    rows = ''.join(f'<tr><td>{y}</td><td>{e(a)}</td><td>{e(o)}</td></tr>' for a, o, y in AWARDS)
    body = f'''<section class="about wrap">
  <div class="about-text">
    <h1>About Myra</h1>
    <div class="prose">
      <p>A lifelong artist, Myra Lehman has been making sculpture for more than thirty years. She works in many materials: alabaster, marble, limestone and soapstone, hardwoods from black walnut to Hawaiian koa, and bronze and clay.</p>
      <p>She studied with Ron Mineo, Sebastiano Mineo and Ira Chaffee at the Art Life Studio, and with Carla Rae Johnson at the County Center. In 1991 she worked at the Barsanti Studio in Pietrasanta, Italy, and returned to study in Carrara in September 2001.</p>
      <p>In 1989 she had a one-person show at the Rye Free Reading Room. Her work was shown at the Mari Gallery in Mamaroneck in 1993, and at Our World Gallery in Stamford, Connecticut, with two painters in May 2001. Her sculptures are in private collections in New York, New Jersey, Connecticut, Ohio, Maryland, Virginia, California and the Netherlands.</p>
      <p>Her work is inspired by travel to museums here and abroad. She follows her ideas toward minimalist abstraction, with attention to line and negative space. The themes are visualizations of mental processes and an expression of the characteristics of the materials.</p>
    </div>
  </div>
  <figure class="about-fig">
    <a href="works/{feat["slug"]}.html">{img(feat, 0, 'lg', r, '', 'eager', '(max-width: 900px) 100vw, 40vw')}</a>
    <figcaption><a href="works/{feat["slug"]}.html">{e(feat["title"])}</a>, {e(feat["material"].lower())}</figcaption>
  </figure>
</section>
<section class="wrap section">
  <h2>Awards</h2>
  <table class="awards"><caption class="sr-only">Awards by year</caption>
    <thead><tr><th scope="col">Year</th><th scope="col">Award</th><th scope="col">Exhibition</th></tr></thead>
    <tbody>{rows}</tbody></table>
</section>'''
    return page(r, 'About', body, active='about', canonical='resume.html')


def contact_page():
    r = ''
    opts = ''.join(f'<option value="{w["slug"]}" data-title="{e(w["title"])}">{e(w["title"])} ({e(w["material"])})</option>'
                   for w in sorted(WORKS, key=lambda x: x['title'].lower()))
    body = f'''<section class="contact wrap">
  <div class="contact-intro">
    <h1>Contact</h1>
    <p>Ask about a sculpture you've seen here, or about commissioning a new piece. Myra replies by email.</p>
    <figure class="contact-fig" id="piece-fig" hidden></figure>
    <p class="direct">Or write directly to <a href="mailto:sculpturemyra@optonline.net">sculpturemyra@optonline.net</a></p>
  </div>
  <form class="form" id="contact-form" novalidate>
    <div class="field">
      <label for="f-piece">What is this about?</label>
      <select id="f-piece" name="piece">
        <option value="">A general question</option>
        <option value="custom">Commissioning a new piece</option>
        <optgroup label="A sculpture on this site">{opts}</optgroup>
      </select>
    </div>
    <div class="field-row">
      <div class="field"><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
      <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
    </div>
    <div class="field-row">
      <div class="field"><label for="f-phone">Phone <span class="opt">(optional)</span></label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
      <div class="field" id="price-field"><label for="f-price">Budget <span class="opt">(optional)</span></label><input id="f-price" name="price" placeholder="e.g. $5,000 to $10,000"></div>
    </div>
    <div class="field"><label for="f-msg">Message</label><textarea id="f-msg" name="msg" rows="6" required></textarea></div>
    <div class="g-recaptcha" data-sitekey="6LfiwHEUAAAAAMUW375uK9w2Sbr72QZz0OtayF4-"></div>
    <p class="form-status" id="form-status" role="status" aria-live="polite"></p>
    <button class="btn" type="submit">Send message</button>
  </form>
</section>
<script type="application/json" id="works-data">{works_json(WORKS)}</script>'''
    return page(r, 'Contact', body, active='contact', canonical='contact.html',
                scripts='<script src="https://www.google.com/recaptcha/api.js" async defer></script>')


def sitemap():
    urls = ['', 'gallery.html', 'resume.html', 'contact.html'] + [f'gallery/{c}.html' for c, _ in CATS] + \
           [f'works/{w["slug"]}.html' for w in WORKS]
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
        ''.join(f'  <url><loc>{SITE_URL}{u}</loc></url>\n' for u in urls) + '</urlset>\n'


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)


if __name__ == '__main__':
    write('index.html', index_page())
    write('gallery.html', gallery_page(''))
    for c, _ in CATS:
        write(f'gallery/{c}.html', gallery_page('../', c))
    for i in range(len(WORKS)):
        write(f'works/{WORKS[i]["slug"]}.html', work_page(i))
    write('resume.html', about_page())
    write('contact.html', contact_page())
    write('sitemap.xml', sitemap())
    print(f'Built {len(WORKS)} work pages + 8 pages')
