// static/js/country-filter.js
// Client-side filtering for campsites by country
(function () {
  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () {
    var select = document.getElementById("countryFilter");
    if (!select) return;

    var cards = Array.prototype.slice.call(document.querySelectorAll(".campsite-card[data-country]"));
    var emptyState = document.getElementById("countryEmptyState");

    function applyFilter() {
      var val = (select.value || "all").toUpperCase();
      var visibleCount = 0;

      for (var i = 0; i < cards.length; i++) {
        var card = cards[i];
        var code = String(card.dataset.country || "").toUpperCase();
        var match = (val === "ALL") || (code === val);
        if (match) {
          card.classList.remove("hidden");
          visibleCount++;
        } else {
          card.classList.add("hidden");
        }
      }

      if (emptyState) {
        if (visibleCount === 0) {
          emptyState.classList.remove("hidden");
        } else {
          emptyState.classList.add("hidden");
        }
      }
    }

    // Initial state: show all
    applyFilter();

    // Change handler
    select.addEventListener("change", applyFilter, false);
  });
})();
