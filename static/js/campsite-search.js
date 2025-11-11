// static/js/campsite-search.js
// Combined client-side filtering for campsites by country, name, and town
(function () {
  function normalize(s) {
    return (s || '').toString().trim().toLowerCase();
  }

  function matchesQuery(card, q) {
    if (!q) return true;
    const nameFromAttr = card.getAttribute('data-name');
    const townFromAttr = card.getAttribute('data-town');

    // Fallbacks if attributes are missing: attempt to read visible text
    const nameText = nameFromAttr || (card.querySelector('[data-campsite-name]')?.textContent) || card.textContent || '';
    const townText = townFromAttr || '';

    const name = normalize(nameText);
    const town = normalize(townText);

    return name.includes(q) || town.includes(q);
  }

  function matchesCountry(card, selected) {
    if (!selected || selected === 'all') return true;
    const country = normalize(card.getAttribute('data-country'));
    return country === selected;
  }

  function applyFilters() {
    const searchInput = document.getElementById('campsiteSearch');
    const countrySelect = document.getElementById('countryFilter');
    const q = normalize(searchInput ? searchInput.value : '');
    const selected = normalize(countrySelect ? countrySelect.value : '');

    const cards = document.querySelectorAll('.campsite-card[data-country]');
    let visibleCount = 0;

    cards.forEach((card) => {
      const visible = matchesCountry(card, selected) && matchesQuery(card, q);
      card.classList.toggle('hidden', !visible);
      if (visible) visibleCount++;
    });

    const emptyState = document.getElementById('emptyState');
    if (emptyState) {
      emptyState.classList.toggle('hidden', visibleCount !== 0);
    }
  }

  function debounce(fn, delay) {
    let t;
    return function () {
      clearTimeout(t);
      t = setTimeout(fn, delay);
    };
  }

  const debouncedApply = debounce(applyFilters, 200);

  document.addEventListener('DOMContentLoaded', function () {
    const countrySelect = document.getElementById('countryFilter');
    const searchInput = document.getElementById('campsiteSearch');

    if (countrySelect) {
      countrySelect.addEventListener('change', debouncedApply);
    }
    if (searchInput) {
      searchInput.addEventListener('input', debouncedApply);
      searchInput.addEventListener('keyup', debouncedApply);
    }

    // Initial apply to respect default country filter state on load
    applyFilters();
  });

  // Expose for other scripts (e.g., country-filter.js) to call
  window.applyCampsiteFilters = applyFilters;
})();
