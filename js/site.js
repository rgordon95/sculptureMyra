/* Sculpture Myra: gallery filters, quick preview viewer, work page views, contact form. */
(function () {
  'use strict';
  var root = document.body.getAttribute('data-root') || '';
  var dataEl = document.getElementById('works-data');
  var works = dataEl ? JSON.parse(dataEl.textContent) : [];
  var bySlug = {};
  works.forEach(function (w) { bySlug[w.slug] = w; });
  var src = function (name, size) { return root + 'img/web/' + (size || 'lg') + '/' + name; };
  var esc = function (s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; };

  /* ---------- Gallery filters ---------- */
  var grid = document.getElementById('grid');
  var chips = document.querySelectorAll('.chip[data-filter]');
  function applyFilter(cat, push) {
    if (!grid) return;
    grid.querySelectorAll('.tile').forEach(function (t) { t.hidden = !!cat && t.dataset.cat !== cat; });
    chips.forEach(function (c) {
      if (c.dataset.filter === cat) c.setAttribute('aria-current', 'true'); else c.removeAttribute('aria-current');
    });
    if (push) history.replaceState(null, '', chips[0] && [].find.call(chips, function (c) { return c.dataset.filter === cat; }).href);
  }
  chips.forEach(function (c) {
    c.addEventListener('click', function (ev) { ev.preventDefault(); applyFilter(c.dataset.filter, true); });
  });
  if (grid && grid.dataset.preset) applyFilter(grid.dataset.preset, false);

  /* ---------- Viewer (quick preview + zoom) ---------- */
  var viewer = document.getElementById('viewer');
  var state = { list: [], i: 0, view: 0 };
  if (viewer) {
    var vImg = document.getElementById('viewer-img');
    var vTitle = document.getElementById('viewer-title');
    var vFacts = document.getElementById('viewer-facts');
    var vThumbs = document.getElementById('viewer-thumbs');
    var vPage = document.getElementById('viewer-page');
    var vAsk = document.getElementById('viewer-ask');
    var vCount = document.getElementById('viewer-count');

    var render = function () {
      var w = state.list[state.i];
      var pic = w.pics[state.view];
      vImg.src = src(pic[0]);
      vImg.width = pic[1]; vImg.height = pic[2];
      vImg.alt = w.title + ', ' + w.material + (state.view ? ' (view ' + (state.view + 1) + ')' : '');
      vTitle.textContent = w.title;
      vFacts.innerHTML = [['Material', w.material], ['Dimensions', w.dimensions], ['Collection', w.cat]]
        .filter(function (r) { return r[1]; })
        .map(function (r) { return '<div><dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd></div>'; }).join('');
      vThumbs.innerHTML = w.pics.length < 2 ? '' : w.pics.map(function (p, k) {
        return '<button type="button" data-view="' + k + '" aria-label="Show view ' + (k + 1) + '"' +
          (k === state.view ? ' aria-current="true"' : '') + '><img src="' + src(p[0], 'sm') + '" alt=""></button>';
      }).join('');
      vPage.href = root + 'works/' + w.slug + '.html';
      vAsk.href = root + 'contact.html?piece=' + w.slug;
      vCount.textContent = (state.i + 1) + ' of ' + state.list.length;
      // warm the neighbours so arrowing feels instant
      [state.i - 1, state.i + 1].forEach(function (k) {
        var n = state.list[(k + state.list.length) % state.list.length];
        if (n) new Image().src = src(n.pics[0][0]);
      });
    };
    var open = function (list, i, view, single) {
      state = { list: list, i: i, view: view || 0 };
      viewer.classList.toggle('single', !!single);
      render();
      if (!viewer.open) viewer.showModal();
    };
    var step = function (d) {
      if (viewer.classList.contains('single') || state.list.length < 2) return;
      state.i = (state.i + d + state.list.length) % state.list.length;
      state.view = 0;
      render();
    };
    viewer.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (b && b.dataset.step) step(+b.dataset.step);
      else if (b && b.dataset.view) { state.view = +b.dataset.view; render(); }
      else if (b && b.classList.contains('v-close')) viewer.close();
      else if (ev.target.classList.contains('viewer-stage')) viewer.close();
    });
    viewer.addEventListener('keydown', function (ev) {
      if (ev.key === 'ArrowRight') step(1);
      if (ev.key === 'ArrowLeft') step(-1);
    });
    var touchX = null;
    viewer.addEventListener('touchstart', function (ev) { touchX = ev.touches[0].clientX; }, { passive: true });
    viewer.addEventListener('touchend', function (ev) {
      if (touchX === null) return;
      var dx = ev.changedTouches[0].clientX - touchX;
      if (Math.abs(dx) > 50) step(dx < 0 ? 1 : -1);
      touchX = null;
    });

    // Tiles open a preview on plain click; modified clicks still open the work's own page.
    document.addEventListener('click', function (ev) {
      var t = ev.target.closest('.tile');
      if (!t || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button !== 0) return;
      var scope = t.closest('.justified');
      var visible = [].filter.call(scope.querySelectorAll('.tile'), function (x) { return !x.hidden; })
        .map(function (x) { return bySlug[x.dataset.slug]; });
      if (!bySlug[t.dataset.slug] || visible.indexOf(undefined) !== -1) return; // not previewable here
      ev.preventDefault();
      open(visible, visible.indexOf(bySlug[t.dataset.slug]));
    });

    /* Work page: thumbnails swap the stage image; clicking the stage opens it full screen. */
    var stage = document.querySelector('.stage-img');
    var zoom = document.getElementById('zoom');
    var current = 0;
    if (stage && works.length === 1) {
      var w = works[0];
      document.querySelectorAll('.thumb').forEach(function (b) {
        b.addEventListener('click', function () {
          current = +b.dataset.i;
          var p = w.pics[current];
          stage.removeAttribute('srcset');
          stage.src = src(p[0]); stage.width = p[1]; stage.height = p[2];
          stage.alt = w.title + ', ' + w.material + (current ? ' (view ' + (current + 1) + ')' : '');
          document.querySelectorAll('.thumb').forEach(function (x) { x.removeAttribute('aria-current'); });
          b.setAttribute('aria-current', 'true');
        });
      });
      zoom.addEventListener('click', function () { open([w], 0, current, true); });
      // "More" tiles on a work page are not in works-data, so they navigate normally.
    }
  }

  /* ---------- Contact form ---------- */
  var form = document.getElementById('contact-form');
  if (form) {
    var sel = document.getElementById('f-piece');
    var fig = document.getElementById('piece-fig');
    var price = document.getElementById('price-field');
    var status = document.getElementById('form-status');
    var syncPiece = function () {
      var w = bySlug[sel.value];
      price.hidden = sel.value === '';
      if (w) {
        fig.innerHTML = '<div class="pic"><img src="' + src(w.pics[0][0], 'sm') + '" alt="' + esc(w.title) + '"></div>' +
          '<figcaption>' + esc(w.title) + ', ' + esc(w.material.toLowerCase()) + '</figcaption>';
        fig.hidden = false;
      } else { fig.hidden = true; fig.innerHTML = ''; }
    };
    var piece = new URLSearchParams(location.search).get('piece');
    if (piece && sel.querySelector('option[value="' + CSS.escape(piece) + '"]')) sel.value = piece;
    sel.addEventListener('change', syncPiece);
    syncPiece();

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      status.className = 'form-status';
      if (!form.checkValidity()) {
        var bad = form.querySelector(':invalid');
        status.textContent = 'Fill in ' + bad.labels[0].textContent.toLowerCase() + ' to send your message.';
        status.className = 'form-status err';
        bad.focus();
        return;
      }
      if (!window.grecaptcha || grecaptcha.getResponse().length === 0) {
        status.textContent = 'Tick "I\'m not a robot" to send your message.';
        status.className = 'form-status err';
        return;
      }
      var fd = new FormData(form);
      var opt = sel.selectedOptions[0];
      var isPiece = sel.value !== '';
      fd.set('piece', sel.value === 'custom' ? 'Custom piece' : (opt.dataset.title || ''));
      var btn = form.querySelector('button[type=submit]');
      btn.disabled = true;
      status.textContent = 'Sending…';
      fetch(root + 'php/' + (isPiece ? 'sculpture_inquiry.php' : 'contact_form.php'), { method: 'POST', body: fd })
        .then(function (res) {
          if (!res.ok) throw new Error(res.status);
          form.reset(); grecaptcha.reset(); syncPiece();
          status.textContent = 'Message sent. Myra will reply by email.';
        })
        .catch(function () {
          status.textContent = 'Your message could not be sent. Email sculpturemyra@optonline.net instead.';
          status.className = 'form-status err';
        })
        .then(function () { btn.disabled = false; });
    });
  }
})();
