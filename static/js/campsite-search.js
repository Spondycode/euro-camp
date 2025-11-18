// static/js/campsite-search.js
// Handles search and filtering integration with pagination API

(function () {
  let debounceTimer;

  function init() {
    const countrySelect = document.getElementById('countryFilter');
    const searchInput = document.getElementById('campsiteSearch');

    if (countrySelect) {
      countrySelect.addEventListener('change', onFiltersChanged);
    }
    
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(onFiltersChanged, 300);
      });
      
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          onFiltersChanged();
        }
      });
    }
  }

  function onFiltersChanged() {
    const countrySelect = document.getElementById('countryFilter');
    const searchInput = document.getElementById('campsiteSearch');
    
    const country = countrySelect ? (countrySelect.value || '').trim() : '';
    const search = searchInput ? (searchInput.value || '').trim() : '';
    
    // Dispatch custom event for pagination controller
    const event = new CustomEvent('ec:filters-changed', {
      detail: { country, search }
    });
    document.dispatchEvent(event);
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
