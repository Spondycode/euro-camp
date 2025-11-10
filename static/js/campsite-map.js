// Campsite map initializer using Leaflet and OpenStreetMap

document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('campsite-map');
  if (!el || typeof L === 'undefined') return;

  const latRaw = el.dataset.lat;
  const lngRaw = el.dataset.lng;
  const name = el.dataset.name || 'Campsite';

  const fallbackEl = document.getElementById('campsite-map-fallback');
  const linkEl = document.getElementById('campsite-map-link');

  const toNum = (v) => {
    const n = parseFloat(v);
    return Number.isFinite(n) ? n : null;
  };

  const lat = toNum(latRaw);
  const lng = toNum(lngRaw);
  const valid = lat !== null && lng !== null && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;

  const osmDirect = (la, ln) => `https://www.openstreetmap.org/?mlat=${la}&mlon=${ln}#map=14/${la}/${ln}`;
  const osmSearch = (q) => `https://www.openstreetmap.org/search?query=${encodeURIComponent(q)}`;

  if (!valid) {
    // Hide map and show fallback link
    el.style.display = 'none';
    if (fallbackEl) {
      const url = name ? osmSearch(name) : 'https://www.openstreetmap.org/';
      fallbackEl.setAttribute('href', url);
      fallbackEl.textContent = 'Open location in OpenStreetMap';
      fallbackEl.removeAttribute('hidden');
    }
    return;
  }

  // Initialize Leaflet map
  const map = L.map(el, { scrollWheelZoom: false, tap: false });
  map.setView([lat, lng], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  L.marker([lat, lng]).addTo(map).bindPopup(name);

  // Show helper link under the map
  if (linkEl) {
    linkEl.setAttribute('href', osmDirect(lat, lng));
    linkEl.textContent = 'Open in OpenStreetMap';
    linkEl.removeAttribute('hidden');
  }
});
