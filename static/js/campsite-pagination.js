// static/js/campsite-pagination.js
// Handles AJAX pagination for campsites list with "Load More" and numbered pagination

(function () {
  const state = {
    endpoint: '/api/campsites/',
    currentPage: 1,
    totalPages: 1,
    country: '',
    search: '',
    isLoading: false,
  };

  const els = {};

  function init() {
    els.gridInitial = document.getElementById('campsites-grid-initial');
    els.gridAppend = document.getElementById('campsites-grid-append');
    els.total = document.getElementById('campsites-total');
    els.loading = document.getElementById('campsites-loading');
    els.wrap = document.getElementById('campsites-pagination');
    els.loadMore = document.getElementById('load-more-btn');
    els.pageNums = document.getElementById('pagination-numbers');

    if (!els.wrap) return; // Not on campsites list page

    // Read initial state from data attributes
    state.endpoint = els.wrap.dataset.endpoint || state.endpoint;
    state.currentPage = parseInt(els.wrap.dataset.currentPage || '1', 10);
    state.totalPages = parseInt(els.wrap.dataset.totalPages || '1', 10);
    state.country = els.wrap.dataset.initialCountry || '';
    state.search = els.wrap.dataset.initialSearch || '';

    bindEvents();
    renderPagination();
    updateLoadMoreState();
    exposeAPI();
  }

  function bindEvents() {
    // Load More button
    if (els.loadMore) {
      els.loadMore.addEventListener('click', () => {
        if (state.isLoading) return;
        const next = state.currentPage + 1;
        if (next <= state.totalPages) {
          fetchPage(next, { append: true });
        }
      });
    }

    // Listen for filter changes from campsite-search.js
    document.addEventListener('ec:filters-changed', (e) => {
      const { country = '', search = '' } = e.detail || {};
      setFilters({ country, search });
      fetchPage(1, { replace: true });
    });
  }

  function setFilters({ country, search }) {
    state.country = (country || '').trim();
    state.search = (search || '').trim();
  }

  function buildQuery(page) {
    const params = new URLSearchParams();
    params.set('page', String(page));
    if (state.country && state.country !== 'all') params.set('country', state.country);
    if (state.search) params.set('search', state.search);
    return `${state.endpoint}?${params.toString()}`;
  }

  async function fetchPage(page, { append = false, replace = false } = {}) {
    try {
      setLoading(true);
      const url = buildQuery(page);
      const res = await fetch(url, { credentials: 'same-origin' });
      
      if (!res.ok) throw new Error(`Failed to load: ${res.status}`);
      
      const data = await res.json();
      state.currentPage = data.current_page || page;
      state.totalPages = data.total_pages || state.totalPages;

      const cards = data.results.map(renderCardHTML).join('');

      if (replace) {
        // Clear initial grid and replace append grid
        if (els.gridInitial) els.gridInitial.innerHTML = '';
        if (els.gridAppend) els.gridAppend.innerHTML = cards;
      } else if (append) {
        // Append to the append grid
        if (els.gridAppend) els.gridAppend.insertAdjacentHTML('beforeend', cards);
      }

      updateTotalCount(data.count);
      renderPagination();
      updateLoadMoreState();

    } catch (err) {
      console.error('Pagination error:', err);
      alert('Something went wrong loading campsites. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function renderCardHTML(c) {
    // Match the exact template structure from templates/campsites/list.html
    const liked = !!c.has_liked;
    const premiumClass = c.is_premium ? 'bg-gradient-to-br from-yellow-50 to-white border-2 border-yellow-400' : 'bg-white';
    const imageUrl = c.image_url ? `${c.image_url}?tr=w-400,h-300,fo-auto,f-auto,q-75` : '';
    
    return `
      <div class="campsite-card ${premiumClass} rounded-lg shadow-md hover:shadow-xl transition overflow-hidden" 
           data-country="${escapeAttr(c.country)}" 
           data-name="${escapeAttr(c.name)}" 
           data-town="${escapeAttr(c.town || '')}">
        ${imageUrl ? `
          <a href="/campsites/${c.id}/" class="block w-full h-48 overflow-hidden relative group">
            <img src="${escapeAttr(imageUrl)}" 
                 alt="${escapeAttr(c.name)}" 
                 class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
            ${c.is_premium ? `
              <div class="absolute top-2 right-2 bg-yellow-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center">
                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                </svg>
                PREMIUM
              </div>
            ` : ''}
          </a>
        ` : ''}
        <div class="p-6">
          <div class="mb-4">
            <div class="flex justify-between items-start mb-2">
              <h2 class="text-2xl font-bold text-gray-800">${escapeHtml(c.name)}</h2>
            </div>
            <p class="text-sm text-gray-500 flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              ${escapeHtml(c.country_name || c.country || '')}
            </p>
          </div>
          
          <p class="text-gray-600 mb-4 line-clamp-3">${escapeHtml((c.description || '').split(' ').slice(0, 20).join(' '))}${(c.description || '').split(' ').length > 20 ? '...' : ''}</p>
          
          <div class="space-y-2 text-sm">
            ${c.phone_number ? `
              <p class="text-gray-700 flex items-center">
                <svg class="w-4 h-4 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                </svg>
                ${escapeHtml(c.phone_number)}
              </p>
            ` : ''}
            
            ${c.website ? `
              <p class="text-gray-700 flex items-center">
                <svg class="w-4 h-4 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
                </svg>
                <a href="${escapeAttr(c.website)}" target="_blank" class="text-green-600 hover:text-green-700 hover:underline">
                  Visit Website
                </a>
              </p>
            ` : ''}
          </div>
          
          <div class="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
            <button class="like-btn flex items-center gap-1 ${liked ? 'text-rose-600' : 'text-gray-500'} hover:text-rose-600 transition cursor-pointer"
                    data-campsite-id="${c.id}"
                    data-like-url="/api/campsites/${c.id}/like/"
                    data-liked="${liked ? 'true' : 'false'}"
                    data-auth-required="false">
              <svg class="heart-outline w-5 h-5 ${liked ? 'hidden' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
              </svg>
              <svg class="heart-solid w-5 h-5 ${liked ? '' : 'hidden'}" fill="currentColor" viewBox="0 0 24 24">
                <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"></path>
              </svg>
              <span class="like-count text-sm font-medium">${c.like_count ?? 0}</span>
            </button>
            <a href="/campsites/${c.id}/" class="text-green-600 hover:text-green-700 font-semibold flex items-center">
              View Details
              <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </a>
          </div>
        </div>
      </div>
    `;
  }

  function renderPagination() {
    if (!els.pageNums) return;
    
    const pages = buildPageList(state.currentPage, state.totalPages);
    const buttons = [];

    // Previous button
    buttons.push(`
      <button class="px-3 py-1 rounded border text-sm ${state.currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'}"
              ${state.currentPage === 1 ? 'disabled' : ''}
              data-page="${state.currentPage - 1}">
        Previous
      </button>
    `);

    // Page numbers
    pages.forEach(p => {
      if (p === '...') {
        buttons.push('<span class="px-2 text-gray-500 select-none">…</span>');
      } else {
        const active = p === state.currentPage;
        buttons.push(`
          <button class="px-3 py-1 rounded border text-sm ${active ? 'bg-blue-600 text-white border-blue-600' : 'hover:bg-gray-50'}"
                  data-page="${p}">
            ${p}
          </button>
        `);
      }
    });

    // Next button
    buttons.push(`
      <button class="px-3 py-1 rounded border text-sm ${state.currentPage === state.totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'}"
              ${state.currentPage === state.totalPages ? 'disabled' : ''}
              data-page="${state.currentPage + 1}">
        Next
      </button>
    `);

    els.pageNums.innerHTML = buttons.join('');

    // Bind click events
    els.pageNums.querySelectorAll('button[data-page]').forEach(btn => {
      btn.addEventListener('click', () => {
        const page = parseInt(btn.getAttribute('data-page'), 10);
        if (!isNaN(page) && page >= 1 && page <= state.totalPages && page !== state.currentPage) {
          fetchPage(page, { replace: true });
          // Scroll to top of appended content
          if (els.gridAppend) {
            els.gridAppend.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      });
    });
  }

  function buildPageList(current, total) {
    if (total <= 1) return [1];
    
    const pages = new Set();
    const edge = 1;  // Always show first and last page
    const around = 2; // Show 2 pages around current

    // First page
    for (let i = 1; i <= Math.min(edge, total); i++) {
      pages.add(i);
    }

    // Pages around current
    for (let i = Math.max(1, current - around); i <= Math.min(total, current + around); i++) {
      pages.add(i);
    }

    // Last page
    for (let i = Math.max(total - edge + 1, 1); i <= total; i++) {
      pages.add(i);
    }

    // Convert to sorted array and add ellipsis
    const sorted = Array.from(pages).sort((a, b) => a - b);
    const result = [];
    
    for (let i = 0; i < sorted.length; i++) {
      result.push(sorted[i]);
      if (i < sorted.length - 1 && sorted[i + 1] > sorted[i] + 1) {
        result.push('...');
      }
    }

    return result;
  }

  function updateTotalCount(count) {
    if (els.total) {
      els.total.textContent = `Total campsites: ${count}`;
    }
  }

  function updateLoadMoreState() {
    if (!els.loadMore) return;
    
    const hasMore = state.currentPage < state.totalPages;
    els.loadMore.disabled = !hasMore || state.isLoading;
  }

  function setLoading(isLoading) {
    state.isLoading = isLoading;
    
    // Toggle loading overlay
    if (els.loading) {
      els.loading.classList.toggle('hidden', !isLoading);
    }
    
    // Toggle button state
    if (els.loadMore) {
      const label = els.loadMore.querySelector('[data-label]');
      const spinner = els.loadMore.querySelector('[data-spinner]');
      
      if (label && spinner) {
        label.classList.toggle('hidden', isLoading);
        spinner.classList.toggle('hidden', !isLoading);
      }
      
      els.loadMore.disabled = isLoading || state.currentPage >= state.totalPages;
    }
  }

  function escapeHtml(str) {
    if (str == null) return '';
    return String(str).replace(/[&<>"']/g, m => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[m]));
  }

  function escapeAttr(str) {
    if (str == null) return '';
    return String(str).replace(/"/g, '&quot;');
  }

  function exposeAPI() {
    // Expose public API for other scripts
    window.CampsitePagination = {
      setFilters,
      loadPage: (page, opts) => fetchPage(page, opts || { replace: true }),
      getState: () => ({ ...state }),
    };
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
