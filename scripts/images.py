"""Generate web-sized images from the originals in img/ for every sculpture in data/sculptures.json.

Writes img/web/lg/<slug>-<n>.jpg (2000px long edge) and img/web/sm/<slug>-<n>.jpg (900px),
and records width/height in data/images.json. Skips files that already exist.
"""
import json, os
from PIL import Image, ImageOps
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZES = {'lg': (2000, 82), 'sm': (900, 78)}
data = json.load(open(os.path.join(ROOT, 'data', 'sculptures.json')))
meta_path = os.path.join(ROOT, 'data', 'images.json')
meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
for d in SIZES: os.makedirs(os.path.join(ROOT, 'img', 'web', d), exist_ok=True)
for s in data:
    for i, src in enumerate(s['images'], 1):
        name = f"{s['slug']}-{i}.jpg"
        outs = {d: os.path.join(ROOT, 'img', 'web', d, name) for d in SIZES}
        if name in meta and all(os.path.exists(p) for p in outs.values()):
            continue
        im = ImageOps.exif_transpose(Image.open(os.path.join(ROOT, src))).convert('RGB')
        for d, (edge, q) in SIZES.items():
            c = im.copy(); c.thumbnail((edge, edge), Image.LANCZOS)
            c.save(outs[d], 'JPEG', quality=q, optimize=True, progressive=True)
        meta[name] = {'src': src, 'w': im.width, 'h': im.height}
        print(name)
json.dump(meta, open(meta_path, 'w'), indent=1, sort_keys=True)
