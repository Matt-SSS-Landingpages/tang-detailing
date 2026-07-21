/* ============================================================
   TANG DETAILING — Shared JS
   ============================================================ */
(function () {
  'use strict';

  /* ---- Nav scroll state ---- */
  var nav = document.querySelector('.nav');
  function onScroll() {
    if (!nav) return;
    if (window.scrollY > 20) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---- Mobile menu ---- */
  var toggle = document.querySelector('.nav-toggle');
  var menu = document.querySelector('.mobile-menu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      toggle.classList.toggle('open', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        menu.classList.remove('open');
        toggle.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
    menu.querySelectorAll('.mm-acc').forEach(function (btn) {
      btn.addEventListener('click', function () {
        btn.parentElement.classList.toggle('open');
      });
    });
  }

  /* ---- Scroll reveal ---- */
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          ro.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach(function (el) { ro.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---- Animated counters ---- */
  function animate(el) {
    var target = parseFloat(el.getAttribute('data-target'));
    var decimals = (el.getAttribute('data-decimals')) ? parseInt(el.getAttribute('data-decimals'), 10) : 0;
    var dur = 1800, start = null;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      var val = target * eased;
      el.textContent = decimals ? val.toFixed(decimals) : Math.floor(val).toLocaleString('en-US');
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = decimals ? target.toFixed(decimals) : Math.floor(target).toLocaleString('en-US');
    }
    requestAnimationFrame(step);
  }
  var counters = document.querySelectorAll('.counter');
  if (counters.length && 'IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { animate(e.target); co.unobserve(e.target); }
      });
    }, { threshold: 0.4 });
    counters.forEach(function (c) { co.observe(c); });
  } else {
    counters.forEach(animate);
  }

  /* ---- Draggable before/after slider ---- */
  document.querySelectorAll('[data-ba]').forEach(function (slider) {
    var handle = slider.querySelector('.ba-handle');
    var after = slider.querySelector('.ba-after');
    var active = false;

    function setPos(clientX) {
      var rect = slider.getBoundingClientRect();
      var x = clientX - rect.left;
      var pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
      after.style.clipPath = 'inset(0 0 0 ' + pct + '%)';
      handle.style.left = pct + '%';
    }
    function down(e) { active = true; slider.classList.add('dragging'); setPos((e.touches ? e.touches[0] : e).clientX); }
    function move(e) { if (!active) return; setPos((e.touches ? e.touches[0] : e).clientX); }
    function up() { active = false; slider.classList.remove('dragging'); }

    slider.addEventListener('mousedown', down);
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    slider.addEventListener('touchstart', down, { passive: true });
    window.addEventListener('touchmove', move, { passive: true });
    window.addEventListener('touchend', up);
  });

  /* ---- Comparison slider ---- */
  document.querySelectorAll('[data-cmp-slider]').forEach(function (root) {
    var slides = root.querySelectorAll('.cmp-slide');
    var dots = root.querySelectorAll('.cmp-dot');
    var tabs = root.querySelectorAll('.cmp-tab');
    var prev = root.querySelector('.cmp-arrow.prev');
    var next = root.querySelector('.cmp-arrow.next');
    var idx = 0;
    function show(i) {
      idx = (i + slides.length) % slides.length;
      slides.forEach(function (s, n) { s.classList.toggle('active', n === idx); });
      dots.forEach(function (d, n) { d.classList.toggle('active', n === idx); });
      tabs.forEach(function (t, n) { t.classList.toggle('active', n === idx); });
    }
    if (prev) prev.addEventListener('click', function () { show(idx - 1); });
    if (next) next.addEventListener('click', function () { show(idx + 1); });
    dots.forEach(function (d, n) { d.addEventListener('click', function () { show(n); }); });
    tabs.forEach(function (t, n) { t.addEventListener('click', function () { show(n); }); });
    show(0);
  });

  /* ---- FAQ accordion ---- */
  document.querySelectorAll('.faq-item').forEach(function (item) {
    var q = item.querySelector('.faq-q');
    if (!q) return;
    q.addEventListener('click', function () {
      var open = item.classList.contains('open');
      var group = item.closest('[data-faq-group]');
      if (group) group.querySelectorAll('.faq-item.open').forEach(function (o) { if (o !== item) o.classList.remove('open'); });
      item.classList.toggle('open', !open);
    });
  });

  /* ---- Why-book click-through carousel (mobile only) ---- */
  var mqMobile = window.matchMedia('(max-width:600px)');
  document.querySelectorAll('.cc-why-scroller').forEach(function (sc) {
    var list = sc.querySelector('.cc-why-list');
    if (!list) return;
    var items = Array.prototype.slice.call(list.querySelectorAll('.cc-why-item'));
    if (items.length < 2) return;

    var arrow = function (dir) {
      return '<svg viewBox="0 0 24 24" stroke-width="2">' +
        (dir === 'prev' ? '<path d="M15 6l-6 6 6 6"/>' : '<path d="M9 6l6 6-6 6"/>') + '</svg>';
    };

    var hint = document.createElement('div');
    hint.className = 'cc-why-hint';
    hint.innerHTML = 'Tap through the benefits ' + arrow('next');

    var nav = document.createElement('div');
    nav.className = 'cc-why-nav';
    var prev = document.createElement('button');
    prev.type = 'button'; prev.className = 'cc-why-arrow'; prev.setAttribute('aria-label', 'Previous'); prev.innerHTML = arrow('prev');
    var next = document.createElement('button');
    next.type = 'button'; next.className = 'cc-why-arrow'; next.setAttribute('aria-label', 'Next'); next.innerHTML = arrow('next');
    var dots = document.createElement('div');
    dots.className = 'cc-why-dots';
    var dotEls = items.map(function (_, i) {
      var d = document.createElement('button');
      d.type = 'button'; d.className = 'cc-why-dot' + (i === 0 ? ' active' : '');
      d.setAttribute('aria-label', 'Benefit ' + (i + 1));
      d.addEventListener('click', function () { go(i); });
      dots.appendChild(d);
      return d;
    });
    nav.appendChild(prev); nav.appendChild(dots); nav.appendChild(next);

    sc.parentNode.insertBefore(hint, sc);
    sc.parentNode.insertBefore(nav, sc.nextSibling);

    var idx = 0;
    function go(i) {
      idx = (i + items.length) % items.length;
      list.scrollTo({ left: items[idx].offsetLeft - list.offsetLeft, behavior: 'smooth' });
      dotEls.forEach(function (d, n) { d.classList.toggle('active', n === idx); });
    }
    prev.addEventListener('click', function () { go(idx - 1); });
    next.addEventListener('click', function () { go(idx + 1); });
    items.forEach(function (it, i) {
      it.addEventListener('click', function () { if (mqMobile.matches) go(i + 1); });
    });
    var st;
    list.addEventListener('scroll', function () {
      clearTimeout(st);
      st = setTimeout(function () {
        var nearest = 0, min = Infinity;
        items.forEach(function (it, i) {
          var d = Math.abs((it.offsetLeft - list.offsetLeft) - list.scrollLeft);
          if (d < min) { min = d; nearest = i; }
        });
        idx = nearest;
        dotEls.forEach(function (d, n) { d.classList.toggle('active', n === idx); });
      }, 90);
    }, { passive: true });
  });

  /* ---- Reviews marquee (duplicate track for seamless loop) ---- */
  document.querySelectorAll('.rev-marquee .rev-track').forEach(function (track) {
    track.innerHTML += track.innerHTML;
  });

  /* ---- Current year ---- */
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
