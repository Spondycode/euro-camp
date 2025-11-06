// static/js/likes.js
// AJAX-based campsite likes functionality

function getCSRFCookie() {
  const name = 'csrftoken=';
  const decoded = decodeURIComponent(document.cookie || '');
  const parts = decoded.split(';');
  for (let c of parts) {
    c = c.trim();
    if (c.startsWith(name)) return c.substring(name.length);
  }
  return '';
}

function updateLikeUI(btn, isLiked, likeCount) {
  btn.dataset.liked = isLiked ? 'true' : 'false';

  const outline = btn.querySelector('.heart-outline');
  const solid = btn.querySelector('.heart-solid');
  if (outline && solid) {
    if (isLiked) {
      outline.classList.add('hidden');
      solid.classList.remove('hidden');
      btn.classList.add('text-rose-600');
      btn.classList.remove('text-gray-500');
    } else {
      solid.classList.add('hidden');
      outline.classList.remove('hidden');
      btn.classList.remove('text-rose-600');
      btn.classList.add('text-gray-500');
    }
  }

  const countEl = btn.querySelector('.like-count');
  if (countEl) countEl.textContent = String(likeCount);
}

async function toggleLike(btn) {
  const url = btn.dataset.likeUrl;
  if (!url) return;

  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFCookie(),
    },
    credentials: 'same-origin',
    body: JSON.stringify({}),
  });

  if (resp.status === 401 || resp.status === 403) {
    const next = encodeURIComponent(window.location.pathname + window.location.search);
    window.location.assign('/login/?next=' + next);
    return;
  }

  if (!resp.ok) {
    throw new Error('Failed to toggle like, status ' + resp.status);
  }

  const data = await resp.json();
  updateLikeUI(btn, Boolean(data.is_liked), Number(data.like_count));
}

document.addEventListener('click', (e) => {
  const btn = e.target.closest('.like-btn');
  if (!btn) return;

  e.preventDefault();
  e.stopPropagation();

  if (btn.dataset.authRequired === 'true') {
    const next = encodeURIComponent(window.location.pathname + window.location.search);
    window.location.assign('/login/?next=' + next);
    return;
  }

  if (btn.dataset.loading === 'true') return; // prevent double-click
  btn.dataset.loading = 'true';

  toggleLike(btn)
    .catch((err) => {
      console.error(err);
      alert('Sorry, we could not update your like right now.');
    })
    .finally(() => {
      btn.dataset.loading = 'false';
    });
});
