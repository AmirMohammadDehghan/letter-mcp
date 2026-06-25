(function () {
  'use strict';

  var storageKey = 'jazzy-theme';
  var root = document.documentElement;

  function systemTheme() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    root.setAttribute('data-jazzy-theme', theme);
    var buttons = document.querySelectorAll('[data-jazzy-theme-toggle]');
    buttons.forEach(function (button) {
      var isDark = theme === 'dark';
      button.setAttribute('aria-pressed', isDark ? 'true' : 'false');
      button.setAttribute('title', isDark ? 'تغییر به تم روشن' : 'تغییر به تم تیره');
      button.setAttribute('aria-label', isDark ? 'تغییر به تم روشن' : 'تغییر به تم تیره');
      var icon = button.querySelector('i');
      if (icon) {
        icon.classList.toggle('fa-sun', isDark);
        icon.classList.toggle('fa-moon', !isDark);
      }
    });
  }

  function currentTheme() {
    try {
      return localStorage.getItem(storageKey) || root.getAttribute('data-jazzy-theme') || systemTheme();
    } catch (error) {
      return root.getAttribute('data-jazzy-theme') || systemTheme();
    }
  }

  function saveTheme(theme) {
    try { localStorage.setItem(storageKey, theme); } catch (error) { /* noop */ }
    applyTheme(theme);
  }

  document.addEventListener('DOMContentLoaded', function () {
    applyTheme(currentTheme());

    document.querySelectorAll('[data-jazzy-theme-toggle]').forEach(function (button) {
      button.addEventListener('click', function () {
        saveTheme(currentTheme() === 'dark' ? 'light' : 'dark');
      });
    });

    if (window.matchMedia) {
      var media = window.matchMedia('(prefers-color-scheme: dark)');
      var onChange = function () {
        try {
          if (!localStorage.getItem(storageKey)) { applyTheme(systemTheme()); }
        } catch (error) {
          applyTheme(systemTheme());
        }
      };
      if (media.addEventListener) { media.addEventListener('change', onChange); }
      else if (media.addListener) { media.addListener(onChange); }
    }
  });
})();


(function () {
  'use strict';

  var sidebarKey = 'jazzy-sidebar-state';
  var desktopQuery = window.matchMedia ? window.matchMedia('(min-width: 992px)') : null;
  var body = document.body;

  function isDesktop() {
    return desktopQuery ? desktopQuery.matches : window.innerWidth >= 992;
  }

  function ensureBackdrop() {
    var backdrop = document.querySelector('.jazzy-sidebar-backdrop');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.className = 'jazzy-sidebar-backdrop';
      backdrop.setAttribute('data-jazzy-sidebar-close', '');
      document.body.appendChild(backdrop);
    }
    return backdrop;
  }

  function savedState() {
    try { return localStorage.getItem(sidebarKey) || 'expanded'; }
    catch (error) { return 'expanded'; }
  }

  function saveState(state) {
    try { localStorage.setItem(sidebarKey, state); }
    catch (error) { /* noop */ }
  }

  function syncButtons() {
    var collapsed = body.classList.contains('sidebar-collapse');
    var opened = body.classList.contains('sidebar-open');
    document.querySelectorAll('[data-jazzy-sidebar-toggle]').forEach(function (button) {
      var desktop = isDesktop();
      button.setAttribute('aria-expanded', desktop ? String(!collapsed) : String(opened));
      button.setAttribute('aria-pressed', desktop ? String(collapsed) : String(opened));
      if (button.classList.contains('jazzy-sidebar-collapse-btn')) {
        button.setAttribute('title', collapsed ? 'باز کردن سایدبار' : 'جمع کردن سایدبار');
        button.setAttribute('aria-label', collapsed ? 'باز کردن سایدبار' : 'جمع کردن سایدبار');
      }
    });
  }

  function applyDesktopState(state) {
    body.classList.remove('sidebar-open');
    body.classList.toggle('sidebar-collapse', state === 'collapsed');
    syncButtons();
  }

  function closeMobileSidebar() {
    body.classList.remove('sidebar-open');
    syncButtons();
  }

  function toggleSidebar(event) {
    if (event) { event.preventDefault(); }
    if (isDesktop()) {
      var collapsed = !body.classList.contains('sidebar-collapse');
      body.classList.toggle('sidebar-collapse', collapsed);
      saveState(collapsed ? 'collapsed' : 'expanded');
    } else {
      body.classList.remove('sidebar-collapse');
      body.classList.toggle('sidebar-open');
    }
    syncButtons();
  }

  document.addEventListener('DOMContentLoaded', function () {
    ensureBackdrop();
    if (isDesktop()) { applyDesktopState(savedState()); }
    else { body.classList.remove('sidebar-collapse', 'sidebar-open'); }

    document.querySelectorAll('[data-jazzy-sidebar-toggle]').forEach(function (button) {
      button.addEventListener('click', toggleSidebar);
    });

    document.addEventListener('click', function (event) {
      if (event.target && event.target.closest('[data-jazzy-sidebar-close]')) {
        closeMobileSidebar();
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') { closeMobileSidebar(); }
    });

    var onResize = function () {
      if (isDesktop()) { applyDesktopState(savedState()); }
      else { body.classList.remove('sidebar-collapse', 'sidebar-open'); syncButtons(); }
    };
    if (desktopQuery && desktopQuery.addEventListener) { desktopQuery.addEventListener('change', onResize); }
    else if (desktopQuery && desktopQuery.addListener) { desktopQuery.addListener(onResize); }
    window.addEventListener('orientationchange', onResize);
  });
})();
