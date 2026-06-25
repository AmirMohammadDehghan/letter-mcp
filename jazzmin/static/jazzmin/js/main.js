(function () {
  'use strict';

  const root = document.documentElement;
  const body = document.body;
  const SIDEBAR_KEY = 'nova-admin-sidebar';
  const THEME_KEY = 'nova-admin-theme';
  const DESKTOP_QUERY = '(min-width: 901px)';
  const CONFIG = window.NOVA_ADMIN_CONFIG || {};
  const docEl = document.documentElement;
  const htmlDir = (docEl.getAttribute('dir') || document.body.getAttribute('data-nova-dir') || 'rtl').toLowerCase();
  const htmlLang = (docEl.getAttribute('lang') || document.body.getAttribute('data-nova-lang') || 'fa').toLowerCase();
  const isRTLPage = htmlDir === 'rtl';
  const isPersianLocale = /^fa($|-|_)/.test(htmlLang) || /^fa($|-|_)/.test((document.body.getAttribute('data-nova-lang') || '').toLowerCase());
  const NOVA_I18N = {
    calendar: isPersianLocale ? 'تقویم' : 'Calendar',
    openCalendar: isPersianLocale ? 'باز کردن تقویم' : 'Open calendar',
    time: isPersianLocale ? 'زمان' : 'Time',
    selectTime: isPersianLocale ? 'انتخاب زمان' : 'Select time',
    lookup: isPersianLocale ? 'جستجو' : 'Lookup'
  };

  const qs = (selector, parent) => (parent || document).querySelector(selector);
  const qsa = (selector, parent) => Array.prototype.slice.call((parent || document).querySelectorAll(selector));
  const isDesktop = () => window.matchMedia(DESKTOP_QUERY).matches;

  function applyTheme(theme) {
    if (theme === 'light' || theme === 'dark') {
      root.setAttribute('data-theme', theme);
      try { localStorage.setItem(THEME_KEY, theme); } catch (e) {}
    }
  }

  function initTheme() {
    let saved = null;
    try { saved = localStorage.getItem(THEME_KEY); } catch (e) {}
    if (saved) {
      applyTheme(saved);
    } else if (CONFIG.themeMode === 'light' || CONFIG.themeMode === 'dark') {
      root.setAttribute('data-theme', CONFIG.themeMode);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      root.setAttribute('data-theme', 'light');
    }
    qsa('[data-nova-theme-toggle]').forEach((btn) => {
      btn.addEventListener('click', () => applyTheme(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light'));
    });
  }

  function setSidebarState(state) {
    if (CONFIG.enableSidebarCollapse === false && state === 'collapsed') state = 'expanded';
    if (!isDesktop() && state === 'collapsed') state = 'expanded';
    const collapsed = isDesktop() && state === 'collapsed';
    const mobileOpen = !isDesktop() && state === 'open-mobile';
    body.classList.toggle('nova-sidebar-collapsed', collapsed);
    body.classList.toggle('nova-sidebar-open', mobileOpen);
    qsa('[data-nova-sidebar-toggle]').forEach((btn) => btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true'));
    if (state !== 'open-mobile') {
      try { localStorage.setItem(SIDEBAR_KEY, collapsed ? 'collapsed' : 'expanded'); } catch (e) {}
    }
  }

  function syncSidebarForViewport() {
    let saved = CONFIG.defaultSidebarState || 'expanded';
    try { saved = localStorage.getItem(SIDEBAR_KEY) || saved; } catch (e) {}
    if (isDesktop()) {
      body.classList.remove('nova-sidebar-open');
      setSidebarState(saved === 'collapsed' ? 'collapsed' : 'expanded');
    } else {
      body.classList.remove('nova-sidebar-collapsed');
      body.classList.remove('nova-sidebar-open');
    }
  }

  function initSidebar() {
    syncSidebarForViewport();
    qsa('[data-nova-sidebar-toggle]').forEach((btn) => {
      btn.addEventListener('click', () => {
        if (!isDesktop()) {
          body.classList.toggle('nova-sidebar-open');
          return;
        }
        if (CONFIG.enableSidebarCollapse === false) return;
        setSidebarState(body.classList.contains('nova-sidebar-collapsed') ? 'expanded' : 'collapsed');
      });
    });
    qsa('[data-nova-mobile-menu]').forEach((btn) => btn.addEventListener('click', () => setSidebarState('open-mobile')));
    qsa('[data-nova-overlay]').forEach((el) => el.addEventListener('click', () => body.classList.remove('nova-sidebar-open')));
    qsa('[data-nova-menu-trigger]').forEach((trigger) => {
      trigger.addEventListener('click', () => {
        if (body.classList.contains('nova-sidebar-collapsed') && isDesktop()) return;
        const group = trigger.closest('[data-nova-menu-group]');
        if (group) group.classList.toggle('is-open');
      });
    });
    let resizeTimer = null;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(syncSidebarForViewport, 120);
    });
  }

  function initActiveNav() {
    const path = window.location.pathname.replace(/\/$/, '');
    let active = null;
    qsa('[data-nova-nav-link]').forEach((link) => {
      const href = (link.getAttribute('href') || '').replace(/\/$/, '');
      if (href && href !== '#' && (href === path || path.indexOf(href + '/') === 0)) active = link;
    });
    if (active) {
      active.classList.add('is-active');
      const group = active.closest('[data-nova-menu-group]');
      if (group) group.classList.add('is-open');
    }
  }

  function initDropdowns() {
    qsa('[data-nova-dropdown-button]').forEach((btn) => {
      btn.addEventListener('click', (event) => {
        event.preventDefault();
        const wrap = btn.closest('[data-nova-dropdown]');
        qsa('[data-nova-dropdown].is-open').forEach((dropdown) => { if (dropdown !== wrap) dropdown.classList.remove('is-open'); });
        if (wrap) wrap.classList.toggle('is-open');
      });
    });
    document.addEventListener('click', (event) => {
      if (!event.target.closest('[data-nova-dropdown]')) qsa('[data-nova-dropdown].is-open').forEach((d) => d.classList.remove('is-open'));
      if (!event.target.closest('[data-nova-time-wrap]') && !event.target.closest('.nova-time-menu')) qsa('.nova-time-menu.is-open').forEach((m) => m.classList.remove('is-open'));
    });
  }

  function initTabsAndCollapses() {
    qsa('#jazzy-tabs a[href^="#"], .nova-tabs a[href^="#"], .nav-tabs a[href^="#"]').forEach((tab) => {
      tab.addEventListener('click', (event) => {
        event.preventDefault();
        const href = tab.getAttribute('href');
        const panel = href ? qs(href) : null;
        if (!panel) return;
        const tabs = tab.closest('#jazzy-tabs, .nova-tabs, .nav-tabs');
        const container = panel.parentElement;
        qsa('a', tabs).forEach((link) => link.classList.remove('active'));
        qsa('.tab-pane', container).forEach((pane) => pane.classList.remove('active', 'show'));
        tab.classList.add('active');
        panel.classList.add('active', 'show');
        if (history.pushState) history.pushState(null, '', href);
      });
    });
    const hash = window.location.hash;
    if (hash) {
      const tab = qs('a[href="' + hash + '"]');
      if (tab) tab.click();
    }
  }

  function initDismiss() {
    qsa('[data-nova-dismiss]').forEach((btn) => btn.addEventListener('click', () => {
      const item = btn.closest('.nova-alert');
      if (item) item.remove();
    }));
  }

  function initRelatedLinks() {
    qsa('.related-lookup').forEach((link) => { if (!link.textContent.trim()) link.textContent = NOVA_I18N.lookup; });
    qsa('.add-another').forEach((link) => { if (!link.textContent.trim()) link.textContent = '+'; });
  }

  function wrapControl(input, className) {
    if (!input || input.parentElement.classList.contains(className)) return input.parentElement;
    const wrap = document.createElement('span');
    wrap.className = className;
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    return wrap;
  }

  function initPersianDatepicker(context) {
    const $ = window.jQuery || (window.django && window.django.jQuery);
    if ($ && $.fn && !$.fn.andSelf && $.fn.addBack) $.fn.andSelf = $.fn.addBack;
    if (!$ || !$.fn || !$.fn.datepicker) return;

    const scope = context || document;
    const selector = [
      'input.vDateField',
      'input.nova-jalali-date',
      'input[data-jalali-datepicker]',
      'input[type="text"][id="id_date"]',
      'input[type="text"][id$="_date"]',
      'input[type="text"][id*="date"]',
      'input[type="text"][name$="_date"]'
    ].join(',');

    $(selector, scope).each(function () {
      if (this.dataset.novaJalaliReady === '1' || this.disabled || this.readOnly) return;
      this.dataset.novaJalaliReady = '1';
      this.autocomplete = 'off';
      this.classList.add('nova-jalali-input');
      try {
        const options = {
          dateFormat: 'yy/mm/dd',
          changeMonth: true,
          changeYear: true,
          yearRange: 'c-80:c+10',
          showButtonPanel: true,
          showOn: 'both',
          buttonText: NOVA_I18N.calendar,
          isRTL: isRTLPage,
          firstDay: isPersianLocale ? 6 : 0,
          beforeShow: function () { setTimeout(() => $('#ui-datepicker-div').appendTo(document.body).css('z-index', 2147483000).addClass('nova-datepicker-visible'), 0); },
          onClose: function () { $('#ui-datepicker-div').removeClass('nova-datepicker-visible'); }
        };
        if (isPersianLocale && window.JalaliDate) options.calendar = window.JalaliDate;
        $(this).datepicker(options);
        const trigger = this.parentNode.querySelector('.ui-datepicker-trigger');
        if (trigger) {
          trigger.setAttribute('type', 'button');
          trigger.setAttribute('aria-label', NOVA_I18N.openCalendar);
          trigger.classList.add('nova-datepicker-trigger');
        }
      } catch (e) {
        this.dataset.novaJalaliReady = '0';
      }
    });
  }

  function initTimePicker(context) {
    const scope = context || document;
    const selector = 'input.vTimeField, input.nova-time-field, input[type="text"][id$="_time"], input[type="text"][name$="_time"]';

    function closeMenus(except) {
      qsa('.nova-time-menu.is-open').forEach((menu) => {
        if (menu !== except) menu.classList.remove('is-open');
      });
    }

    function placeMenu(input, menu) {
      const rect = input.getBoundingClientRect();
      const menuWidth = Math.min(236, Math.max(210, rect.width + 64));
      const viewportW = window.innerWidth || document.documentElement.clientWidth;
      const viewportH = window.innerHeight || document.documentElement.clientHeight;
      menu.style.width = menuWidth + 'px';
      menu.style.position = 'fixed';
      menu.style.zIndex = '2147483000';
      menu.style.maxHeight = Math.min(292, Math.max(190, viewportH - rect.bottom - 18)) + 'px';
      let top = rect.bottom + 8;
      if (top + 210 > viewportH && rect.top > 230) top = Math.max(12, rect.top - 220);
      menu.style.top = Math.round(top) + 'px';
      if (isRTLPage) {
        let right = Math.max(12, viewportW - rect.right);
        if (right + menuWidth > viewportW - 12) right = Math.max(12, viewportW - menuWidth - 12);
        menu.style.right = Math.round(right) + 'px';
        menu.style.left = 'auto';
      } else {
        let left = Math.max(12, rect.left);
        if (left + menuWidth > viewportW - 12) left = Math.max(12, viewportW - menuWidth - 12);
        menu.style.left = Math.round(left) + 'px';
        menu.style.right = 'auto';
      }
    }

    qsa(selector, scope).forEach((input) => {
      if (input.dataset.novaTimeReady === '1' || input.disabled || input.readOnly) return;
      input.dataset.novaTimeReady = '1';
      input.autocomplete = 'off';
      input.classList.add('nova-time-input');
      const wrap = wrapControl(input, 'nova-time-wrap');
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'nova-time-trigger';
      btn.textContent = NOVA_I18N.time;
      btn.setAttribute('aria-label', NOVA_I18N.selectTime);
      const menu = document.createElement('div');
      menu.className = 'nova-time-menu nova-time-menu-portal';
      const times = [];
      for (let h = 0; h < 24; h += 1) {
        for (let m = 0; m < 60; m += 15) times.push(String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0'));
      }
      times.forEach((time) => {
        const item = document.createElement('button');
        item.type = 'button';
        item.textContent = time;
        item.addEventListener('click', () => {
          input.value = time;
          input.dispatchEvent(new Event('change', { bubbles: true }));
          menu.classList.remove('is-open');
          input.focus();
        });
        menu.appendChild(item);
      });
      wrap.appendChild(btn);
      document.body.appendChild(menu);
      btn.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        const willOpen = !menu.classList.contains('is-open');
        closeMenus(menu);
        if (willOpen) {
          placeMenu(input, menu);
          menu.classList.add('is-open');
        } else {
          menu.classList.remove('is-open');
        }
      });
      input.addEventListener('focus', () => {
        if (menu.classList.contains('is-open')) placeMenu(input, menu);
      });
      window.addEventListener('scroll', () => {
        if (menu.classList.contains('is-open')) placeMenu(input, menu);
      }, true);
      window.addEventListener('resize', () => {
        if (menu.classList.contains('is-open')) placeMenu(input, menu);
      });
    });
  }

  function initDateTimePickers(context) {
    initPersianDatepicker(context);
    initTimePicker(context);
  }

  document.addEventListener('DOMContentLoaded', function () {
    initTheme();
    initSidebar();
    initActiveNav();
    initDropdowns();
    initTabsAndCollapses();
    initDismiss();
    initRelatedLinks();
    initDateTimePickers(document);
  });

  document.addEventListener('formset:added', function (event) {
    initDateTimePickers(event.target || document);
  });

  window.NovaAdmin = window.NovaAdmin || {};
  window.NovaAdmin.direction = htmlDir;
  window.NovaAdmin.language = htmlLang;
  window.NovaAdmin.initPersianDatepicker = initPersianDatepicker;
  window.NovaAdmin.initTimePicker = initTimePicker;
})();
