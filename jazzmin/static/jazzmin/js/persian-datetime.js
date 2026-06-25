(function (window, document) {
  'use strict';

  var $ = (window.django && window.django.jQuery) || window.jQuery;
  var hasJalali = typeof window.JalaliDate === 'function';

  function toEnglishDigits(value) {
    return String(value || '')
      .replace(/[۰-۹]/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'.indexOf(d); })
      .replace(/[٠-٩]/g, function (d) { return '٠١٢٣٤٥٦٧٨٩'.indexOf(d); })
      .replace(/\u200c/g, '')
      .trim();
  }

  function toPersianDigits(value) {
    return String(value || '').replace(/\d/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'[Number(d)]; });
  }

  function pad(number) {
    number = parseInt(number, 10);
    return number < 10 ? '0' + number : String(number);
  }

  function parseDateParts(value) {
    var normalized = toEnglishDigits(value).replace(/[.]/g, '/').replace(/-/g, '/');
    var match = normalized.match(/^(\d{2,4})\/(\d{1,2})\/(\d{1,2})$/);
    if (!match) { return null; }
    var year = parseInt(match[1], 10);
    if (year < 100) { year += year > 60 ? 1300 : 1400; }
    return {
      year: year,
      month: parseInt(match[2], 10),
      day: parseInt(match[3], 10)
    };
  }

  function parseGregorian(value) {
    var parts = parseDateParts(value);
    if (!parts || parts.year < 1700) { return null; }
    if (parts.month < 1 || parts.month > 12 || parts.day < 1 || parts.day > 31) { return null; }
    return new Date(parts.year, parts.month - 1, parts.day);
  }

  function parseJalali(value) {
    var parts = parseDateParts(value);
    if (!parts || parts.year >= 1700 || !hasJalali) { return null; }
    if (parts.month < 1 || parts.month > 12 || parts.day < 1 || parts.day > 31) { return null; }
    return new window.JalaliDate(parts.year, parts.month - 1, parts.day);
  }

  function gregorianToJalaliString(date) {
    if (!date || !hasJalali) { return ''; }
    var jalali = new window.JalaliDate(date);
    return toPersianDigits(jalali.getFullYear() + '/' + pad(jalali.getMonth() + 1) + '/' + pad(jalali.getDate()));
  }

  function jalaliToGregorianString(value) {
    var jalali = parseJalali(value);
    if (!jalali || !jalali.getGregorianDate) { return toEnglishDigits(value); }
    var gregorian = jalali.getGregorianDate();
    return gregorian.getFullYear() + '-' + pad(gregorian.getMonth() + 1) + '-' + pad(gregorian.getDate());
  }

  function normalizeDateForDisplay(input) {
    if (!input || !hasJalali) { return; }
    var value = toEnglishDigits(input.value);
    if (!value) { return; }
    var gregorian = parseGregorian(value);
    if (gregorian) {
      input.value = gregorianToJalaliString(gregorian);
      input.dataset.jazzyPersianDate = 'jalali';
      return;
    }
    var jalali = parseJalali(value);
    if (jalali) {
      input.value = toPersianDigits(jalali.getFullYear() + '/' + pad(jalali.getMonth() + 1) + '/' + pad(jalali.getDate()));
      input.dataset.jazzyPersianDate = 'jalali';
    }
  }

  function normalizeDateForSubmit(input) {
    if (!input || !input.value || !hasJalali) { return; }
    var value = toEnglishDigits(input.value);
    var gregorian = parseGregorian(value);
    if (gregorian) {
      input.value = gregorian.getFullYear() + '-' + pad(gregorian.getMonth() + 1) + '-' + pad(gregorian.getDate());
      return;
    }
    var jalali = parseJalali(value);
    if (jalali) { input.value = jalaliToGregorianString(value); }
  }

  function decorateDateInputs() {
    var inputs = document.querySelectorAll('input.vDateField, input[type="date"], input[data-jazzy-persian-date]');
    inputs.forEach(function (input) {
      if (input.dataset.jazzyDateReady === '1') { return; }
      input.dataset.jazzyDateReady = '1';
      if (input.type === 'date') {
        try { input.type = 'text'; } catch (error) { /* keep native date when browser blocks conversion */ }
      }
      input.classList.add('jazzy-persian-date-field');
      input.setAttribute('autocomplete', 'off');
      input.setAttribute('inputmode', 'numeric');
      if (!input.getAttribute('placeholder')) { input.setAttribute('placeholder', '۱۴۰۳/۰۱/۰۱'); }
      normalizeDateForDisplay(input);
      input.addEventListener('blur', function () { normalizeDateForDisplay(input); });
      input.addEventListener('change', function () { normalizeDateForDisplay(input); });

      if ($ && $.fn && $.fn.datepicker && hasJalali) {
        try {
          $(input).datepicker('destroy');
        } catch (error) { /* not initialized */ }
        $(input).datepicker({
          dateFormat: 'yy/mm/dd',
          changeMonth: true,
          changeYear: true,
          showButtonPanel: true,
          firstDay: 6,
          isRTL: true,
          currentText: 'امروز',
          closeText: 'بستن',
          onSelect: function () {
            input.dataset.jazzyPersianDate = 'jalali';
            window.setTimeout(function () { normalizeDateForDisplay(input); }, 0);
          }
        });
      }
    });
  }

  function normalizeTimeValue(value) {
    var normalized = toEnglishDigits(value).replace(/[.]/g, ':').trim();
    var match = normalized.match(/^(\d{1,2})(?::(\d{1,2}))?(?::(\d{1,2}))?$/);
    if (!match) { return normalized; }
    var hour = Math.min(23, Math.max(0, parseInt(match[1] || '0', 10)));
    var minute = Math.min(59, Math.max(0, parseInt(match[2] || '0', 10)));
    var second = Math.min(59, Math.max(0, parseInt(match[3] || '0', 10)));
    return pad(hour) + ':' + pad(minute) + ':' + pad(second);
  }

  var activeTimeInput = null;
  var timePanel = null;

  function setTime(input, value) {
    input.value = normalizeTimeValue(value);
    input.dispatchEvent(new Event('change', { bubbles: true }));
    hideTimePanel();
  }

  function buildTimePanel() {
    if (timePanel) { return timePanel; }
    timePanel = document.createElement('div');
    timePanel.className = 'jazzy-time-panel';
    timePanel.hidden = true;
    timePanel.innerHTML = '' +
      '<div class="jazzy-time-panel__head"><span>انتخاب زمان</span><button type="button" class="jazzy-time-panel__close" aria-label="بستن">×</button></div>' +
      '<div class="jazzy-time-panel__grid"></div>' +
      '<div class="jazzy-time-panel__custom">' +
      '<input type="number" min="0" max="23" step="1" data-hour placeholder="ساعت" aria-label="ساعت">' +
      '<input type="number" min="0" max="59" step="1" data-minute placeholder="دقیقه" aria-label="دقیقه">' +
      '<button type="button" data-apply>ثبت</button>' +
      '</div>';
    document.body.appendChild(timePanel);

    var grid = timePanel.querySelector('.jazzy-time-panel__grid');
    ['00:00:00', '06:00:00', '08:00:00', '09:00:00', '12:00:00', '15:00:00', '18:00:00', '21:00:00', '23:59:00'].forEach(function (time) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'jazzy-time-panel__option';
      button.textContent = toPersianDigits(time.slice(0, 5));
      button.dataset.time = time;
      grid.appendChild(button);
    });

    timePanel.addEventListener('click', function (event) {
      var close = event.target.closest('.jazzy-time-panel__close');
      if (close) { hideTimePanel(); return; }
      var option = event.target.closest('.jazzy-time-panel__option');
      if (option && activeTimeInput) { setTime(activeTimeInput, option.dataset.time); return; }
      var apply = event.target.closest('[data-apply]');
      if (apply && activeTimeInput) {
        var hour = timePanel.querySelector('[data-hour]').value || '0';
        var minute = timePanel.querySelector('[data-minute]').value || '0';
        setTime(activeTimeInput, hour + ':' + minute + ':00');
      }
    });
    return timePanel;
  }

  function positionPanel(input) {
    var panel = buildTimePanel();
    var rect = input.getBoundingClientRect();
    var top = rect.bottom + window.scrollY + 8;
    var left = rect.left + window.scrollX;
    var width = Math.min(304, window.innerWidth - 24);
    if (left + width > window.scrollX + window.innerWidth - 12) {
      left = window.scrollX + window.innerWidth - width - 12;
    }
    if (left < window.scrollX + 12) { left = window.scrollX + 12; }
    panel.style.top = top + 'px';
    panel.style.left = left + 'px';
  }

  function showTimePanel(input) {
    activeTimeInput = input;
    var panel = buildTimePanel();
    var current = normalizeTimeValue(input.value || '00:00:00').split(':');
    panel.querySelector('[data-hour]').value = parseInt(current[0], 10) || 0;
    panel.querySelector('[data-minute]').value = parseInt(current[1], 10) || 0;
    positionPanel(input);
    panel.hidden = false;
  }

  function hideTimePanel() {
    if (timePanel) { timePanel.hidden = true; }
    activeTimeInput = null;
  }

  function decorateTimeInputs() {
    var inputs = document.querySelectorAll('input.vTimeField, input[type="time"], input[data-jazzy-persian-time]');
    inputs.forEach(function (input) {
      if (input.dataset.jazzyTimeReady === '1') { return; }
      input.dataset.jazzyTimeReady = '1';
      if (input.type === 'time') {
        try { input.type = 'text'; } catch (error) { /* keep native time when browser blocks conversion */ }
      }
      input.classList.add('jazzy-persian-time-field');
      input.setAttribute('autocomplete', 'off');
      input.setAttribute('inputmode', 'numeric');
      if (!input.getAttribute('placeholder')) { input.setAttribute('placeholder', 'HH:MM:SS'); }
      input.addEventListener('blur', function () { if (input.value) { input.value = normalizeTimeValue(input.value); } });

      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn btn-outline-secondary jazzy-time-trigger';
      button.setAttribute('aria-label', 'انتخاب زمان');
      button.setAttribute('title', 'انتخاب زمان');
      button.innerHTML = '<i class="far fa-clock" aria-hidden="true"></i>';
      input.insertAdjacentElement('afterend', button);
      button.addEventListener('click', function (event) {
        event.preventDefault();
        showTimePanel(input);
      });
    });
  }

  function normalizeAllForSubmit(event) {
    var form = event.target;
    if (!form || !form.querySelectorAll) { return; }
    form.querySelectorAll('input.vDateField, input[type="date"], input[data-jazzy-persian-date]').forEach(normalizeDateForSubmit);
    form.querySelectorAll('input.vTimeField, input[type="time"], input[data-jazzy-persian-time]').forEach(function (input) {
      if (input.value) { input.value = normalizeTimeValue(input.value); }
    });
  }

  function init() {
    decorateDateInputs();
    decorateTimeInputs();
    document.addEventListener('submit', normalizeAllForSubmit, true);
    document.addEventListener('click', function (event) {
      if (!timePanel || timePanel.hidden) { return; }
      if (event.target.closest('.jazzy-time-panel') || event.target.closest('.jazzy-time-trigger')) { return; }
      hideTimePanel();
    });
    document.addEventListener('keydown', function (event) { if (event.key === 'Escape') { hideTimePanel(); } });
    window.addEventListener('resize', function () { if (activeTimeInput) { positionPanel(activeTimeInput); } });
    window.addEventListener('scroll', function () { if (activeTimeInput) { positionPanel(activeTimeInput); } }, true);
  }

  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', init); }
  else { init(); }
})(window, document);
