/* Main JavaScript for Masjid Website */

document.addEventListener('DOMContentLoaded', function () {

    // ── Sidebar Toggle (Panel) ─────────────────────────────────
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');

    const backdrop = document.getElementById('sidebarBackdrop');
    if (sidebarToggle && sidebar) {
        const setOpen = function (open) {
            sidebar.classList.toggle('show', open);
            if (backdrop) backdrop.classList.toggle('show', open);
            sidebarToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        };
        sidebarToggle.addEventListener('click', function () { setOpen(!sidebar.classList.contains('show')); });
        if (backdrop) backdrop.addEventListener('click', function () { setOpen(false); });
        document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
    }

    // ── Navbar Scroll Effect ───────────────────────────────────
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        const onScroll = function () { navbar.classList.toggle('scrolled', window.scrollY > 8); };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    // ── Prayer boards (hitung mundur sholat berikutnya) ────────
    document.querySelectorAll('[data-prayer-board]').forEach(initPrayerBoard);

    // ── Jadwal bulanan: gulir ke baris hari ini ────────────────
    document.querySelectorAll('.table-scroll').forEach(function (box) {
        const today = box.querySelector('tr.is-today');
        if (today) box.scrollTop = Math.max(0, today.offsetTop - 120);
    });

    // ── Auto-dismiss Alerts ────────────────────────────────────
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // ── Add form-control class to login form inputs ────────────
    const loginInputs = document.querySelectorAll('.login-card input');
    loginInputs.forEach(function (input) {
        input.classList.add('form-control');
    });
});

function initPrayerBoard(board) {
    const cells = Array.from(board.querySelectorAll('[data-time]'));
    const prayers = cells.filter(function (c) { return c.dataset.prayer && c.dataset.time; });
    if (!prayers.length) return;
    const nameEl = board.querySelector('[data-next-name]');
    const timeEl = board.querySelector('[data-next-time]');
    const countEl = board.querySelector('[data-next-countdown]');
    const pad = function (n) { return String(n).padStart(2, '0'); };
    const fmt = function (d) { return pad(d.getHours()) + ':' + pad(d.getMinutes()); };

    function tick() {
        const now = new Date();
        let next = null, nextTime = null, tomorrow = false;
        for (const c of prayers) {
            const t = new Date(c.dataset.time);
            if (t > now) { next = c; nextTime = t; break; }
        }
        if (!next) {  // setelah Isya: Subuh besok (perkiraan +24 jam)
            next = prayers[0];
            nextTime = new Date(new Date(next.dataset.time).getTime() + 864e5);
            tomorrow = true;
        }
        cells.forEach(function (c) {
            const t = new Date(c.dataset.time);
            c.classList.toggle('is-next', c === next && !tomorrow);
            c.classList.toggle('is-past', !tomorrow && t <= now && c !== next);
        });
        if (tomorrow) next.classList.add('is-next');
        const diff = Math.max(0, nextTime - now);
        const h = Math.floor(diff / 36e5), m = Math.floor((diff % 36e5) / 6e4), s = Math.floor((diff % 6e4) / 1e3);
        if (nameEl) nameEl.textContent = next.dataset.prayer + (tomorrow ? ' ' + (board.dataset.tomorrowLabel || 'besok') : '');
        const tEl = next.querySelector('.prayer-cell-time');  // jam lokal masjid, bukan zona waktu peramban
        if (timeEl) timeEl.textContent = tEl ? tEl.textContent : fmt(nextTime);
        const L = board.dataset;
        if (countEl) countEl.textContent = (h ? h + ' ' + (L.lH || 'jam') + ' ' : '') + m + ' ' + (L.lM || 'menit') + ' ' + pad(s) + ' ' + (L.lS || 'detik lagi');
    }
    tick();
    setInterval(tick, 1000);
}
