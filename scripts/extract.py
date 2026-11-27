"""One-off: extract sculpture data from the legacy gallery pages into data/sculptures.json."""
import re, json, os, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = {f.lower(): f for d in ['img/stone','img/wood','img/Other'] for f in [d+'/'+x for x in os.listdir(os.path.join(ROOT,d))]}
def resolve(src):
    p = src.replace('../','').replace('./','')
    return files.get(p.lower())
def slugify(s):
    return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
out, seen = [], {}
for cat in ['stone','wood','other']:
    src = open(os.path.join(ROOT,'gallery',cat+'.html'),encoding='utf-8').read()
    parts = re.split(r'<div class="card[ "]', src)[1:]
    for p in parts:
        t = re.search(r'card-title[^>]*>(.*?)</h4>', p, re.S)
        if not t: continue
        title = html.unescape(t.group(1)).strip().strip('"').strip()
        mat = re.search(r'Material:\s*</strong>\s*(.*?)\s*</p>', p, re.S)
        dim = re.search(r'Dimensions:\s*</strong>\s*(.*?)\s*</p>', p, re.S)
        imgs = []
        for s in re.findall(r'<img[^>]*src="([^"]+)"', p):
            r = resolve(s)
            if r and r not in imgs: imgs.append(r)
            elif not r: print('MISSING', title, s)
        slug = slugify(title)
        if slug in seen:
            slug = slugify(title+' '+(mat.group(1) if mat else cat))
        seen[slug]=1
        out.append(dict(slug=slug,title=title,category=cat,
            material=re.sub(r'\s+',' ',html.unescape(mat.group(1))).strip() if mat else '',
            dimensions=re.sub(r'""','"',re.sub(r'\s+',' ',html.unescape(dim.group(1)))).strip() if dim else '',
            images=imgs))
os.makedirs(os.path.join(ROOT,'data'),exist_ok=True)
json.dump(out, open(os.path.join(ROOT,'data','sculptures.json'),'w'), indent=2)
print(len(out))
