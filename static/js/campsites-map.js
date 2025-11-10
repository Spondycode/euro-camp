// Campsites map initializer using Leaflet and OpenStreetMap
// Supports two modes: country view (all campsites in a country) and radius view (100km radius)

(function () {
  const dataEl = document.getElementById("map-data");
  if (!dataEl) return;
  
  const config = JSON.parse(dataEl.textContent || "{}");
  const loadingEl = document.getElementById("map-loading");

  // Initialize map
  const map = L.map("campsites-map", {
    center: [config.center?.lat || 54.5260, config.center?.lng || 15.2551],
    zoom: 6,
    scrollWheelZoom: true,
  });

  // Add tile layer (OpenStreetMap)
  const tileConf = config.tile || {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "&copy; OpenStreetMap contributors",
  };
  L.tileLayer(tileConf.url, { 
    attribution: tileConf.attribution, 
    maxZoom: 19 
  }).addTo(map);

  // Optional marker clustering if plugin is available
  const group = (typeof L.markerClusterGroup !== 'undefined') 
    ? L.markerClusterGroup() 
    : L.featureGroup();

  // Custom icons for center campsite (radius mode)
  const defaultIcon = new L.Icon.Default();
  
  // For the center campsite, we'll use a distinct styling
  const createCenterIcon = () => {
    return L.divIcon({
      className: 'custom-center-marker',
      html: '<div style="background-color: #ef4444; width: 25px; height: 41px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); border: 3px solid #fff; box-shadow: 0 3px 10px rgba(0,0,0,0.3);"></div>',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
    });
  };

  const centerId = config.centerCampsite?.id || null;

  // Add markers for each campsite
  (config.campsites || []).forEach((c) => {
    if (typeof c.lat !== "number" || typeof c.lng !== "number") return;

    const isCenter = centerId && c.id === centerId && config.mode === "radius";
    const marker = L.marker([c.lat, c.lng], { 
      icon: isCenter ? createCenterIcon() : defaultIcon 
    });

    // Popup content
    const popupHtml = `
      <div class="p-2">
        <div class="font-semibold text-base mb-1">${c.name}${isCenter ? ' <span class="text-xs text-red-600">(Center)</span>' : ''}</div>
        ${c.country ? `<div class="text-xs text-gray-600 mb-1"><svg class="w-3 h-3 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>${c.country}</div>` : ""}
        <div class="text-xs text-gray-600 mb-2"><svg class="w-3 h-3 inline mr-1" fill="currentColor" viewBox="0 0 20 20"><path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"></path></svg>Likes: ${c.likes || 0}</div>
        ${c.url ? `<a class="text-xs text-green-600 hover:text-green-700 font-medium hover:underline" href="${c.url}">View Details →</a>` : ""}
      </div>
    `;
    
    marker.bindPopup(popupHtml, { 
      closeButton: true,
      maxWidth: 250 
    });
    group.addLayer(marker);
  });

  group.addTo(map);

  // Optional: Add radius circle for radius mode
  if (config.mode === "radius" && config.center && config.radius_km) {
    L.circle([config.center.lat, config.center.lng], {
      radius: config.radius_km * 1000, // Convert km to meters
      color: "#ef4444",
      fillColor: "#ef4444",
      fillOpacity: 0.1,
      weight: 2,
      dashArray: '5, 10'
    }).addTo(map);
  }

  // Fit bounds if we have markers; fallback to provided center
  const bounds = group.getBounds();
  if (bounds.isValid()) {
    map.fitBounds(bounds, { padding: [30, 30], maxZoom: 13 });
  } else if (config.center) {
    map.setView([config.center.lat, config.center.lng], config.mode === "radius" ? 10 : 6);
  }

  // Country dropdown handler (Scenario A)
  const countrySelect = document.getElementById("countrySelect");
  if (countrySelect) {
    countrySelect.addEventListener("change", (e) => {
      const value = e.target.value;
      const url = new URL(window.location.href);
      if (value) {
        url.searchParams.set("country", value);
      } else {
        url.searchParams.delete("country");
      }
      url.searchParams.delete("campsite_id"); // Ensure Scenario A
      window.location.href = url.toString();
    });
  }

  // Hide loading overlay
  if (loadingEl) {
    loadingEl.style.display = "none";
  }
})();
