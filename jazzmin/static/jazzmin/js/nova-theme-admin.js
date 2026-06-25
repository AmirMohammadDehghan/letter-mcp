(function () {
  'use strict';
  function enhanceColorInputs(context) {
    var root = context || document;
    var inputs = Array.prototype.slice.call(root.querySelectorAll('input.nova-color-input[type="color"]'));
    inputs.forEach(function (input) {
      if (input.dataset.novaColorReady === '1') return;
      input.dataset.novaColorReady = '1';
      var wrap = document.createElement('span');
      wrap.className = 'nova-color-wrap';
      var text = document.createElement('input');
      text.type = 'text';
      text.className = 'nova-color-hex';
      text.value = input.value || '#000000';
      text.setAttribute('dir', 'ltr');
      text.setAttribute('maxlength', '7');
      input.parentNode.insertBefore(wrap, input);
      wrap.appendChild(input);
      wrap.appendChild(text);
      input.addEventListener('input', function () { text.value = input.value; });
      text.addEventListener('input', function () {
        var value = text.value.trim();
        if (/^#[0-9a-fA-F]{6}$/.test(value)) {
          input.value = value;
          input.dispatchEvent(new Event('input', { bubbles: true }));
          input.dispatchEvent(new Event('change', { bubbles: true }));
        }
      });
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { enhanceColorInputs(document); });
  } else {
    enhanceColorInputs(document);
  }
})();
