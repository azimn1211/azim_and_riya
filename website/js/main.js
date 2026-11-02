/* Azim & Riya — Nikah invitation: intro card, motion, auto-scroll and details. */
(() => {
  'use strict';

  const CONFIG = {
    nikah: new Date('2026-11-19T11:30:00+05:30'),
    nikahEnd: new Date('2026-11-19T12:00:00+05:30'),
    whatsapp: '',                    // Azim's WhatsApp, country code without +, e.g. '919876543210'; empty hides Confirm Attendance
    scrollSpeed: 50,                 // auto-scroll pace in px/s
    scrollDelay: 2000,               // pause after the card opens
    parallax: 3,                     // depth strength of drifting flowers (1 = subtle)
    // To show the 3D photo gallery, list images here, e.g. ['assets/photos/1.jpg', 'assets/photos/2.jpg']
    photos: [],
    places: {
      // Pinned by coordinates: a text search for the masjid lands on a different mosque nearby.
      masjid: {
        name: 'Vallakkadavu Juma Masjid',
        addr: 'Vallakkadavu Road, Vallakkadavu, Thiruvananthapuram',
        at: '8.4779911,76.9305458',
      },
      venue: {
        name: 'Vallakkadavu Convention Centre',
        addr: 'Valiyapally Juma Masjid Road, Vallakkadavu, Thiruvananthapuram',
        at: '8.4712179,76.9260925',
      },
      reception: {
        name: 'Sim Auditorium',
        addr: 'Vizhinjam Harbour Road, Kovalam',
        at: '8.3871837,76.985373',
      },
    },
  };

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const rand = (a, b) => a + Math.random() * (b - a);
  const pick = (list) => list[Math.floor(Math.random() * list.length)];
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const maxScroll = () => document.documentElement.scrollHeight - window.innerHeight;
  const guest = (new URLSearchParams(location.search).get('to') || '').trim().slice(0, 60);

  document.documentElement.classList.remove('no-js');
  document.body.classList.add('is-locked');
  $('#page').inert = true;
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  window.scrollTo(0, 0);

  // ---------------------------------------------------------------------------
  // Sway: one image becomes three stacked, masked layers (root / middle / tip).
  // Each layer rotates around the joint below it, so the rotations compound and
  // the branch bends like a stem in a breeze instead of swinging stiffly.
  // ---------------------------------------------------------------------------
  function buildWhips() {
    $$('img.sway').forEach((img) => {
      const dur = parseFloat(img.dataset.dur || 5);
      const whip = document.createElement('span');
      whip.className = 'whip';
      whip.style.setProperty('--amp', img.dataset.amp || 2);
      whip.style.setProperty('--dur', `${dur}s`);
      whip.style.setProperty('--delay', `${img.dataset.delay ?? -rand(0, dur).toFixed(2)}s`);
      img.replaceWith(whip);
      img.removeAttribute('class');
      const mid = document.createElement('span');
      const tip = document.createElement('span');
      mid.className = 'whip__mid';
      tip.className = 'whip__tip';
      tip.append(img.cloneNode());
      mid.append(img.cloneNode(), tip);
      whip.append(img, mid);
    });
    if (!('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => en.target.classList.toggle('is-idle', !en.isIntersecting));
    }, { rootMargin: '120px' });
    $$('.whip').forEach((w) => io.observe(w));
  }

  // ---------------------------------------------------------------------------
  // Drifting petals, little flowers and eight-pointed stars
  // ---------------------------------------------------------------------------
  function drift(layer, count, o) {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < count; i += 1) {
      const el = document.createElement('span');
      const dur = rand(...o.dur);
      el.className = o.cls;
      el.innerHTML = `<svg><use href="#${pick(o.shapes)}"/></svg>`;
      el.style.left = `${rand(0, 100)}%`;
      el.style.color = pick(o.colors);
      el.style.fontSize = `${rand(...o.size).toFixed(1)}px`;
      el.style.setProperty('--sway', `${rand(-34, 34).toFixed(0)}px`);
      el.style.setProperty('--o', rand(...o.opacity).toFixed(2));
      el.style.setProperty('--dur', `${dur.toFixed(1)}s`);
      el.style.setProperty('--delay', `${(-rand(0, dur)).toFixed(1)}s`);
      frag.append(el);
    }
    layer.append(frag);
  }

  function burst(cx, cy) {
    const layer = $('#intro-burst');
    const colors = ['#e7c97f', '#f0b68a', '#f6e7cf', '#b9b5cd', '#e9a37a'];
    for (let i = 0; i < 28; i += 1) {
      const el = document.createElement('span');
      const a = rand(0, Math.PI * 2);
      const d = rand(110, 380);
      el.className = 'burst';
      el.innerHTML = `<svg><use href="#${pick(['i-flower6', 'i-petal', 'i-star8-solid'])}"/></svg>`;
      el.style.left = `${cx}px`;
      el.style.top = `${cy}px`;
      el.style.color = pick(colors);
      el.style.fontSize = `${rand(12, 26).toFixed(0)}px`;
      el.style.filter = 'drop-shadow(0 0 6px currentColor)';
      el.style.setProperty('--dx', `${(Math.cos(a) * d).toFixed(0)}px`);
      el.style.setProperty('--dy', `${(Math.sin(a) * d).toFixed(0)}px`);
      el.style.setProperty('--r0', `${rand(-40, 40).toFixed(0)}deg`);
      el.style.setProperty('--r1', `${(rand(90, 360) * (Math.random() < 0.5 ? -1 : 1)).toFixed(0)}deg`);
      el.style.setProperty('--delay', `${rand(0, 0.25).toFixed(2)}s`);
      layer.append(el);
    }
  }

  // ---------------------------------------------------------------------------
  // Intro: seal breaks, flowers fly at the viewer, card lifts away
  // ---------------------------------------------------------------------------
  function intro() {
    const el = $('#intro');
    if (guest) {
      $('#intro-guest span').textContent = guest;
      $('#intro-guest').hidden = false;
    }
    if (!reduceMotion) {
      drift($('#intro-ambient'), 18, {
        cls: 'amb',
        shapes: ['i-flower6', 'i-flower6', 'i-petal', 'i-star8-solid'],
        colors: ['#e7c97f', '#f0b68a', '#efe7d6', '#b9b5cd', '#d8bf86'],
        size: [9, 22], opacity: [0.35, 0.7], dur: [18, 26],
      });
    }
    $('#open-btn').addEventListener('click', () => {
      if (el.classList.contains('is-opening')) return;
      el.classList.add('is-opening');
      const seal = $('#seal').getBoundingClientRect();
      const t = reduceMotion ? 0 : 1;
      setTimeout(() => {
        if (!reduceMotion) burst(seal.left + seal.width / 2, seal.top + seal.height / 2);
        el.classList.add('is-away');
      }, 500 * t);
      setTimeout(openPage, 900 * t);
      setTimeout(() => { el.hidden = true; }, 1750 * t + 50);
    });
  }

  function openPage() {
    document.body.classList.remove('is-locked');
    $('#page').inert = false;
    window.scrollTo(0, 0);
    reveal();
    if (!reduceMotion) {
      drift($('#petals'), 9, {
        cls: 'petal',
        shapes: ['i-petal', 'i-petal', 'i-flower6', 'i-star8-solid'],
        colors: ['#e7a678', '#c9a65c', '#8b87a6', '#efc7b8', '#d8bf86'],
        size: [8, 16], opacity: [0.28, 0.55], dur: [20, 30],
      });
    }
    setTimeout(() => autoScroll.start(), CONFIG.scrollDelay);
  }

  // ---------------------------------------------------------------------------
  // Scroll reveal and parallax
  // ---------------------------------------------------------------------------
  function reveal() {
    const els = $$('[data-reveal]');
    if (reduceMotion || !('IntersectionObserver' in window)) {
      els.forEach((e) => e.classList.add('is-in'));
      return;
    }
    // "ink" text starts fully clipped, which IntersectionObserver reads as zero
    // area, so those are triggered by their (unclipped) parent instead.
    const groups = new Map();
    els.forEach((e) => {
      const target = e.dataset.reveal === 'ink' ? e.parentElement : e;
      groups.set(target, [...(groups.get(target) || []), e]);
    });
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        groups.get(en.target).forEach((e) => e.classList.add('is-in'));
        io.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    groups.forEach((_, target) => io.observe(target));
  }

  function parallax() {
    const items = $$('[data-speed]').map((el) => ({
      el,
      speed: parseFloat(el.dataset.speed) * CONFIG.parallax,
      centre: 0,
      selfCentred: el.classList.contains('deco'),   // .deco sits on its anchor via translate(-50%, -50%)
    }));
    if (reduceMotion || !items.length) return;
    let queued = false;
    // Resting centres are cached in page coordinates: reading layout inside the
    // scroll loop, between transform writes, would force a reflow per element.
    const update = () => {
      queued = false;
      const y = window.scrollY;
      const vh = window.innerHeight;
      items.forEach(({ el, speed, centre }) => {
        const c = centre - y;
        if (c < -vh || c > vh * 2) return;
        el.style.transform = `translate3d(0, ${((c - vh / 2) * -speed).toFixed(1)}px, 0)`;
      });
    };
    const queue = () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(update);
    };
    const measure = () => {
      const y = window.scrollY;
      items.forEach((it) => {
        const { el } = it;
        it.centre = el.offsetParent.getBoundingClientRect().top + y + el.offsetTop
          + (it.selfCentred ? 0 : el.offsetHeight / 2);
      });
      queue();
    };
    window.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', measure);
    if ('ResizeObserver' in window) new ResizeObserver(measure).observe($('.sheet'));
    measure();
  }

  // ---------------------------------------------------------------------------
  // Auto-scroll: drifts down the page after opening. Scrolling by hand pauses
  // it, a tap on the page toggles it, and it stops at the end.
  // ---------------------------------------------------------------------------
  let toastTimer = 0;
  function toast(msg, ms = 2600) {
    const t = $('#toast');
    t.textContent = msg;
    t.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('is-on'), ms);
  }

  const autoScroll = (() => {
    const btn = $('#scroll-toggle');
    let state = 'idle';            // idle | playing | paused | done
    let pos = 0;
    let last = 0;
    let raf = 0;
    let touchY = null;

    function setState(s) {
      state = s;
      btn.hidden = s === 'idle';
      const icon = { playing: 'i-pause', paused: 'i-play', done: 'i-up' }[s] || 'i-play';
      btn.querySelector('use').setAttribute('href', `#${icon}`);
      btn.setAttribute('aria-label',
        { playing: 'Pause auto-scroll', paused: 'Resume auto-scroll', done: 'Back to top' }[s] || '');
    }
    function frame(now) {
      if (state !== 'playing') return;
      // rAF passes the frame's start time, which can precede performance.now() from play()
      const dt = Math.max(0, Math.min(0.05, (now - last) / 1000));
      last = now;
      if (Math.abs(window.scrollY - pos) > 3) pos = window.scrollY;   // moved by something else
      pos += CONFIG.scrollSpeed * dt;
      const max = maxScroll();
      if (pos >= max) {
        window.scrollTo(0, max);
        setState('done');
        return;
      }
      window.scrollTo(0, pos);
      raf = requestAnimationFrame(frame);
    }
    function play() {
      if (reduceMotion) return;
      if (maxScroll() - window.scrollY < 4) { setState('done'); return; }
      pos = window.scrollY;
      last = performance.now();
      setState('playing');
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(frame);
    }
    function pause() {
      if (state !== 'playing') return;
      cancelAnimationFrame(raf);
      setState('paused');
    }

    window.addEventListener('touchstart', (e) => { touchY = e.touches[0].clientY; }, { passive: true });
    window.addEventListener('touchmove', (e) => {
      if (state === 'playing' && touchY !== null && Math.abs(e.touches[0].clientY - touchY) > 8) pause();
    }, { passive: true });
    window.addEventListener('keydown', (e) => {
      if (e.target.closest('button, a, input, textarea, select')) return;
      if (['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', ' '].includes(e.key)) pause();
    });
    window.addEventListener('blur', () => {           // focus moved into the map iframe
      if (document.activeElement?.tagName === 'IFRAME') pause();
    });
    document.addEventListener('click', (e) => {
      if (state === 'idle' || e.target.closest('#scroll-toggle, .intro')) return;
      if (e.target.closest('a, button, input, textarea, select, label, iframe, .map, .gallery__stage')) {
        pause();
        return;
      }
      if (state === 'done') return;
      if (state === 'playing') {
        pause();
        toast('Paused · tap anywhere to continue');
      } else {
        play();
        toast('Scrolling · tap to pause', 1600);
      }
    });
    btn.addEventListener('click', () => {
      if (state === 'done') {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        setState('paused');
      } else if (state === 'playing') {
        pause();
      } else {
        play();
      }
    });
    let ringQueued = false;
    const ring = () => {
      ringQueued = false;
      const max = maxScroll();
      btn.style.setProperty('--p', max > 0 ? Math.min(1, window.scrollY / max).toFixed(3) : 0);
      if (state === 'done' && max - window.scrollY > 40) setState('paused');
      else if (state === 'paused' && max - window.scrollY < 4) setState('done');
    };
    window.addEventListener('scroll', () => {
      if (ringQueued) return;
      ringQueued = true;
      requestAnimationFrame(ring);
    }, { passive: true });

    return {
      start() {
        if (reduceMotion) return;
        play();
        if (state === 'playing') toast('Scrolling for you · tap anywhere to pause');
      },
      pause,
    };
  })();

  // ---------------------------------------------------------------------------
  // Smooth wheel: a mouse wheel moves the page in coarse ~100px steps, which
  // makes the parallax flowers jump. Wheel input sets a target instead and the
  // page eases toward it. Touch, keyboard and scrollbar stay native.
  // ---------------------------------------------------------------------------
  function smoothWheel() {
    if (reduceMotion) return;
    let target = 0;
    let current = 0;
    let last = 0;
    let raf = 0;
    const step = (now) => {
      // something else moved the page (scrollbar, keys, back-to-top): let it win
      if (Math.abs(window.scrollY - Math.round(current)) > 2) { raf = 0; return; }
      const dt = Math.max(0, Math.min(0.05, (now - last) / 1000));
      last = now;
      current += (target - current) * (1 - Math.exp(-dt * 9));
      if (Math.abs(target - current) < 0.4) current = target;
      window.scrollTo(0, current);
      raf = current === target ? 0 : requestAnimationFrame(step);
    };
    window.addEventListener('wheel', (e) => {
      if (e.ctrlKey || e.defaultPrevented || document.body.classList.contains('is-locked')) return;
      if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
      e.preventDefault();
      autoScroll.pause();
      const unit = e.deltaMode === 1 ? 40 : e.deltaMode === 2 ? window.innerHeight : 1;
      if (!raf) {
        current = target = window.scrollY;
        last = performance.now();
      }
      target = Math.max(0, Math.min(maxScroll(), target + e.deltaY * unit));
      if (!raf) raf = requestAnimationFrame(step);
    }, { passive: false });
  }

  // ---------------------------------------------------------------------------
  // Details
  // ---------------------------------------------------------------------------
  function countdown() {
    const grid = $('#countdown');
    const done = $('#countdown-done');
    const cells = Object.fromEntries($$('[data-unit]', grid).map((b) => [b.dataset.unit, b]));
    const shown = {};
    let timer = 0;
    const tick = () => {
      const ms = CONFIG.nikah - Date.now();
      if (ms <= 0) {
        clearInterval(timer);
        grid.hidden = true;
        done.hidden = false;
        done.textContent = Date.now() - CONFIG.nikah < 12 * 3600e3
          ? 'Alhamdulillah — the blessed day is here'
          : 'Alhamdulillah — Bārakallāhu lakumā';
        return;
      }
      const s = Math.floor(ms / 1000);
      const vals = { d: Math.floor(s / 86400), h: Math.floor((s % 86400) / 3600), m: Math.floor((s % 3600) / 60), s: s % 60 };
      Object.entries(vals).forEach(([k, v]) => {
        const txt = k === 'd' ? String(v) : String(v).padStart(2, '0');
        if (shown[k] === txt) return;
        shown[k] = txt;
        cells[k].textContent = txt;
        cells[k].classList.remove('tick');
        void cells[k].offsetWidth;   // restart the tick animation
        cells[k].classList.add('tick');
      });
    };
    tick();
    timer = setInterval(tick, 1000);
  }

  function calendar() {
    const year = 2026;
    const month = 10;                                  // November
    const lead = (new Date(year, month, 1).getDay() + 6) % 7;   // Monday first
    const days = new Date(year, month + 1, 0).getDate();
    let html = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'].map((d) => `<span class="dow">${d}</span>`).join('');
    html += '<span class="day"></span>'.repeat(lead);
    for (let d = 1; d <= days; d += 1) {
      html += d === 19
        ? '<span class="day day--big" title="Nikah day"><svg aria-hidden="true"><use href="#i-heart"/></svg><span>19</span></span>'
        : `<span class="day">${d}</span>`;
    }
    $('#calendar').innerHTML = html;
  }

  function addToCalendar() {
    const btn = $('#add-cal-btn');
    const menu = $('#add-cal-menu');
    const stamp = (d) => d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
    const title = 'Nikah of Azim & Riya';
    const where = 'Vallakkadavu Juma Masjid, Vallakkadavu Road, Thiruvananthapuram';
    const url = location.href.split(/[?#]/)[0];
    const details = `Nikah at Vallakkadavu Juma Masjid (near Airport), 11:30 – 12:00.\nVenue: Vallakkadavu Convention Centre.\nWedding reception: Sim Auditorium, Vizhinjam Harbour Road, Kovalam.\n${url}`;
    $('#gcal-link').href = `https://calendar.google.com/calendar/render?${new URLSearchParams({
      action: 'TEMPLATE', text: title, dates: `${stamp(CONFIG.nikah)}/${stamp(CONFIG.nikahEnd)}`,
      details, location: where, ctz: 'Asia/Kolkata',
    })}`;
    const esc = (s) => s.replace(/\\/g, '\\\\').replace(/,/g, '\\,').replace(/;/g, '\\;').replace(/\n/g, '\\n');
    const ics = [
      'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Azim & Riya//Nikah//EN', 'CALSCALE:GREGORIAN',
      'BEGIN:VEVENT', 'UID:azim-riya-nikah-20261119@invitation', `DTSTAMP:${stamp(new Date())}`,
      `DTSTART:${stamp(CONFIG.nikah)}`, `DTEND:${stamp(CONFIG.nikahEnd)}`,
      `SUMMARY:${esc(title)}`, `LOCATION:${esc(where)}`, `DESCRIPTION:${esc(details)}`,
      'BEGIN:VALARM', 'TRIGGER:-PT3H', 'ACTION:DISPLAY', `DESCRIPTION:${esc(title)}`, 'END:VALARM',
      'END:VEVENT', 'END:VCALENDAR',
    ].join('\r\n');
    $('#ics-link').href = `data:text/calendar;charset=utf-8,${encodeURIComponent(ics)}`;

    const close = () => { menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); };
    btn.addEventListener('click', () => {
      const open = menu.hidden;
      menu.hidden = !open;
      btn.setAttribute('aria-expanded', String(open));
    });
    menu.addEventListener('click', close);
    document.addEventListener('click', (e) => { if (!e.target.closest('.add-cal')) close(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  }

  function rsvp() {
    if (!CONFIG.whatsapp) return;
    $('#rsvp').hidden = false;
    const who = guest ? `This is ${guest}. Insha Allah, we will` : 'Insha Allah, I will';
    const msg = `Assalamu Alaikum! ${who} attend the Nikah of Azim & Riya on Thursday, 19 November 2026.`;
    $('#rsvp-btn').href = `https://wa.me/${CONFIG.whatsapp}?text=${encodeURIComponent(msg)}`;
  }

  function venue() {
    const frame = $('#map-frame');
    const set = (key, load) => {
      const p = CONFIG.places[key];
      $('#place-name').textContent = p.name;
      $('#place-addr').textContent = p.addr;
      $('#directions').href = `https://www.google.com/maps/dir/?api=1&destination=${p.at}`;
      frame.dataset.src = `https://maps.google.com/maps?q=${p.at}&z=17&output=embed`;
      frame.title = `Map of ${p.name}`;
      if (load) frame.src = frame.dataset.src;
      $$('.tab').forEach((t) => {
        const on = t.dataset.place === key;
        t.classList.toggle('is-active', on);
        t.setAttribute('aria-selected', String(on));
      });
    };
    $$('.tab').forEach((t) => t.addEventListener('click', () => set(t.dataset.place, true)));
    set('masjid', false);
    if (!('IntersectionObserver' in window)) { frame.src = frame.dataset.src; return; }
    const io = new IntersectionObserver(([en]) => {
      if (!en.isIntersecting) return;
      if (!frame.getAttribute('src')) frame.src = frame.dataset.src;
      io.disconnect();
    }, { rootMargin: '700px 0px' });
    io.observe(frame);
  }

  // Optional 3D cover-flow gallery, built only when CONFIG.photos has images
  function gallery() {
    const section = $('#gallery');
    if (!CONFIG.photos.length) { section.remove(); return; }
    section.hidden = false;
    const stage = $('#gallery-stage');
    const items = CONFIG.photos.map((src, i) => {
      const el = document.createElement('div');
      el.className = 'gallery__item';
      el.innerHTML = `<img src="${src}" alt="Photo ${i + 1}" loading="lazy">`;
      stage.append(el);
      return el;
    });
    const n = items.length;
    let cur = 0;
    const layout = () => {
      items.forEach((el, i) => {
        let k = i - cur;
        if (k > n / 2) k -= n;
        if (k < -n / 2) k += n;
        const a = Math.abs(k);
        el.style.transform = `translateX(${k * 60}%) translateZ(${-150 * a}px) rotateY(${45 * k}deg) scale(${a ? (a === 1 ? 0.85 : 0.7) : 1})`;
        el.style.opacity = [1, 0.75, 0.45][a] ?? 0;
        el.style.zIndex = String(100 - a);
      });
      $('#gallery-count').textContent = `${cur + 1} / ${n}`;
    };
    const go = (d) => { cur = (cur + d + n) % n; layout(); };
    items.forEach((el, i) => el.addEventListener('click', () => { cur = i; layout(); }));
    let x0 = null;
    stage.addEventListener('pointerdown', (e) => { x0 = e.clientX; });
    stage.addEventListener('pointerup', (e) => {
      if (x0 !== null && Math.abs(e.clientX - x0) > 40) go(e.clientX < x0 ? 1 : -1);
      x0 = null;
    });
    setInterval(() => { if (!document.hidden) go(1); }, 3800);
    layout();
  }

  buildWhips();
  calendar();
  countdown();
  addToCalendar();
  rsvp();
  venue();
  gallery();
  parallax();
  smoothWheel();
  intro();
})();
