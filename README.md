# Sculpture Myra

Static site for Myra Lehman's sculpture. Every piece has a preview (click any image in a grid) and its own page under `works/`.

## Editing

All sculpture info lives in `data/sculptures.json` (title, category `stone`/`wood`/`other`, material, dimensions, and original photos under `img/`).

```sh
python3 scripts/images.py   # after adding/changing photos: makes web-sized copies in img/web/ (needs Pillow)
python3 scripts/build.py    # regenerates every HTML page and sitemap.xml
python3 -m http.server      # preview at http://localhost:8000
```

Generated pages: `index.html`, `gallery.html`, `gallery/*.html`, `works/*.html`, `resume.html` (About), `contact.html`.
Hand-written assets: `css/site.css`, `js/site.js`. Don't edit the generated HTML directly; edit `scripts/build.py`.

`dist/` is the output of the old gulp build and is no longer generated.
