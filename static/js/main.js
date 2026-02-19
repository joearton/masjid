/* Main JavaScript for Masjid Website */

document.addEventListener('DOMContentLoaded', function () {

    // ── Sidebar Toggle (Panel) ─────────────────────────────────
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });

        // Close sidebar on outside click (mobile)
        document.addEventListener('click', function (e) {
            if (window.innerWidth < 992) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            }
        });
    }

    // ── Navbar Scroll Effect ───────────────────────────────────
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // ── Auto-dismiss Alerts ────────────────────────────────────
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // ── Prayer Time Countdown ──────────────────────────────────
    updatePrayerCountdown();

    // ── Add form-control class to login form inputs ────────────
    const loginInputs = document.querySelectorAll('.login-card input');
    loginInputs.forEach(function (input) {
        input.classList.add('form-control');
    });
});

function updatePrayerCountdown() {
    const countdownEl = document.getElementById('prayerCountdown');
    if (!countdownEl) return;

    const times = JSON.parse(countdownEl.dataset.times || '{}');
    const now = new Date();
    const todayStr = now.toISOString().split('T')[0];

    let nextPrayer = null;
    let nextTime = null;

    for (const [name, time] of Object.entries(times)) {
        const [h, m] = time.split(':').map(Number);
        const prayerDate = new Date(now);
        prayerDate.setHours(h, m, 0, 0);

        if (prayerDate > now) {
            if (!nextTime || prayerDate < nextTime) {
                nextPrayer = name;
                nextTime = prayerDate;
            }
        }
    }

    if (nextPrayer && nextTime) {
        const diff = nextTime - now;
        const hours = Math.floor(diff / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);
        countdownEl.textContent = `${nextPrayer}: ${hours}j ${minutes}m lagi`;
    }
}
