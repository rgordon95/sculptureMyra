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

  /* ---------- Viewer (quick preview + zoom) ----------
     Arrows, arrow keys and swipes step through the angles of the open sculpture only. */
  var viewer = document.getElementById('viewer');
  var state = { w: null, view: 0 };
  var wrap = function (i, n) { return (i + n) % n; };
  var onSwipe = function (el, fn) {
    var x = null;
    el.addEventListener('touchstart', function (ev) { x = ev.touches[0].clientX; }, { passive: true });
    el.addEventListener('touchend', function (ev) {
      if (x === null) return;
      var dx = ev.changedTouches[0].clientX - x;
      if (Math.abs(dx) > 50) fn(dx < 0 ? 1 : -1);
      x = null;
    });
  };
  if (viewer) {
    var vImg = document.getElementById('viewer-img');
    var vTitle = document.getElementById('viewer-title');
    var vFacts = document.getElementById('viewer-facts');
    var vThumbs = document.getElementById('viewer-thumbs');
    var vPage = document.getElementById('viewer-page');
    var vAsk = document.getElementById('viewer-ask');
    var vCount = document.getElementById('viewer-count');

    var render = function () {
      var w = state.w;
      var pic = w.pics[state.view];
      vImg.src = src(pic[0]);
      vImg.width = pic[1]; vImg.height = pic[2];
      vImg.alt = w.title + ', ' + w.material + (state.view ? ' (angle ' + (state.view + 1) + ')' : '');
      vThumbs.querySelectorAll('button').forEach(function (b) {
        if (+b.dataset.view === state.view) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
      });
      vCount.textContent = 'Angle ' + (state.view + 1) + ' of ' + w.pics.length;
      // warm the neighbouring angles so stepping feels instant
      if (w.pics.length > 1) {
        new Image().src = src(w.pics[wrap(state.view + 1, w.pics.length)][0]);
        new Image().src = src(w.pics[wrap(state.view - 1, w.pics.length)][0]);
      }
    };
    var open = function (w, view, single) {
      state = { w: w, view: view || 0 };
      viewer.classList.toggle('single', !!single);
      viewer.classList.toggle('one-view', w.pics.length < 2);
      vTitle.textContent = w.title;
      vFacts.innerHTML = [['Material', w.material], ['Dimensions', w.dimensions], ['Collection', w.cat]]
        .filter(function (r) { return r[1]; })
        .map(function (r) { return '<div><dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd></div>'; }).join('');
      vThumbs.innerHTML = w.pics.length < 2 ? '' : w.pics.map(function (p, k) {
        return '<button type="button" data-view="' + k + '" aria-label="Show angle ' + (k + 1) + '">' +
          '<img src="' + src(p[0], 'sm') + '" alt=""></button>';
      }).join('');
      vPage.href = root + 'works/' + w.slug + '.html';
      vAsk.href = root + 'contact.html?piece=' + w.slug;
      render();
      if (!viewer.open) viewer.showModal();
    };
    var step = function (d) {
      if (!state.w || state.w.pics.length < 2) return;
      state.view = wrap(state.view + d, state.w.pics.length);
      render();
      if (onViewerStep) onViewerStep(state.view);
    };
    var onViewerStep = null;
    viewer.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (b && b.dataset.step) step(+b.dataset.step);
      else if (b && b.dataset.view) { state.view = +b.dataset.view; render(); if (onViewerStep) onViewerStep(state.view); }
      else if (b && b.classList.contains('v-close')) viewer.close();
      else if (ev.target.classList.contains('viewer-stage')) viewer.close();
    });
    viewer.addEventListener('keydown', function (ev) {
      if (ev.key === 'ArrowRight') { ev.preventDefault(); step(1); }
      if (ev.key === 'ArrowLeft') { ev.preventDefault(); step(-1); }
    });
    onSwipe(viewer, step);

    // Tiles open a preview on plain click; modified clicks still open the work's own page.
    document.addEventListener('click', function (ev) {
      var t = ev.target.closest('.tile');
      if (!t || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button !== 0) return;
      var w = bySlug[t.dataset.slug];
      if (!w || !document.getElementById('grid') || !t.closest('#grid')) return; // e.g. "More" tiles navigate
      ev.preventDefault();
      open(w, 0);
    });

    /* Work page: arrows, thumbnails, keys and swipes change the angle; clicking the photo opens it full screen. */
    var stage = document.querySelector('.stage-img');
    var zoom = document.getElementById('zoom');
    if (stage && works.length === 1) {
      var w = works[0];
      var current = 0;
      var count = document.getElementById('stage-count');
      var thumbs = document.querySelectorAll('.thumb');
      var show = function (i) {
        current = wrap(i, w.pics.length);
        var p = w.pics[current];
        stage.removeAttribute('srcset');
        stage.src = src(p[0]); stage.width = p[1]; stage.height = p[2];
        stage.alt = w.title + ', ' + w.material + (current ? ' (angle ' + (current + 1) + ')' : '');
        thumbs.forEach(function (x) {
          if (+x.dataset.i === current) x.setAttribute('aria-current', 'true'); else x.removeAttribute('aria-current');
        });
        if (count) count.textContent = 'Angle ' + (current + 1) + ' of ' + w.pics.length;
        if (w.pics.length > 1) new Image().src = src(w.pics[wrap(current + 1, w.pics.length)][0]);
      };
      thumbs.forEach(function (b) { b.addEventListener('click', function () { show(+b.dataset.i); }); });
      document.querySelectorAll('[data-stage-step]').forEach(function (b) {
        b.addEventListener('click', function () { show(current + +b.dataset.stageStep); });
      });
      if (w.pics.length > 1) {
        onSwipe(zoom, function (d) { show(current + d); });
        document.addEventListener('keydown', function (ev) {
          if (viewer.open || /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) return;
          if (ev.key === 'ArrowRight') show(current + 1);
          if (ev.key === 'ArrowLeft') show(current - 1);
        });
      }
      onViewerStep = show; // keep the page in sync with the angle viewed full screen
      zoom.addEventListener('click', function () { open(w, current, true); });
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
