(function () {
  'use strict';
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.search-filter, .search-filter-mptt').forEach(field => {
      const updateName = () => {
        const option = field.options ? field.options[field.selectedIndex] : null;
        const name = option ? option.getAttribute('data-name') : null;
        if (name) field.setAttribute('name', name); else field.removeAttribute('name');
      };
      field.addEventListener('change', updateName);
      updateName();
    });
  });
})();
