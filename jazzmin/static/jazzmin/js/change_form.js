(function () {
  'use strict';
  function fixSelectorHeight() {
    document.querySelectorAll('.selector .selector-chosen').forEach(chosen => {
      const available = chosen.parentElement ? chosen.parentElement.querySelector('.selector-available') : null;
      const chosenSelect = chosen.querySelector('select');
      const availableSelect = available ? available.querySelector('select') : null;
      if (chosenSelect && availableSelect) chosenSelect.style.minHeight = availableSelect.offsetHeight + 'px';
    });
  }
  document.addEventListener('DOMContentLoaded', () => {
    fixSelectorHeight();
    document.querySelectorAll('.inline-related fieldset.module .add-row a, div.add-row > a').forEach(a => a.classList.add('nova-btn', 'secondary', 'sm'));
    document.body.addEventListener('change', e => {
      if (e.target && e.target.matches('.related-widget-wrapper select')) {
        const event = new Event('django:update-related', { cancelable: true });
        e.target.dispatchEvent(event);
        if (!event.defaultPrevented && typeof window.updateRelatedObjectLinks !== 'undefined') window.updateRelatedObjectLinks(e.target);
      }
    });
  });
  if (window.django && django.jQuery) django.jQuery(document).on('formset:added', fixSelectorHeight);
})();
