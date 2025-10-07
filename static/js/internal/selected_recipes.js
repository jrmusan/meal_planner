// JS for selected_recipes swipe/tap behavior
// Marks ingredient as used by POSTing to /update-ingredient/<id>

(function () {
  'use strict';

  // Inject required CSS for swipe animation so template doesn't need inline styles
  (function injectStyles() {
  const css = `
  .swipe-row { cursor: pointer; transition: transform 150ms ease; }
  /* swiping now nudges right */
  .swipe-row.swiping { transform: translateX(12px); }
  /* removed slides right and fades out */
  .swipe-row.removed { transform: translateX(120%); opacity: 0; transition: transform 300ms ease, opacity 300ms ease; }
  .swipe-hint { font-size: 0.85em; color: #666; margin-bottom: 8px; }
  `;
    const style = document.createElement('style');
    style.setAttribute('type', 'text/css');
    style.textContent = css;
    document.head.appendChild(style);
  })();

  // Send the POST to mark ingredient used and reload on success
  function sendMarkUsedRequest(ingredientId) {
    if (!ingredientId) return;
    console.log('marking used', ingredientId);
    $.ajax({
      type: 'POST',
      url: '/update-ingredient/' + ingredientId,
      success: function () { location.reload(); },
      error: function (xhr, status, err) { console.error('Failed to mark used', err); }
    });
  }

  function markUsedWithAnimation(row) {
    if (!row || row.dataset._animating) return;
    row.dataset._animating = '1';
    const id = row.getAttribute('data-ingredient-id');
    row.classList.add('removed');

    // Wait for transition to finish or fallback after 400ms
    let called = false;
    function finish() {
      if (called) return; called = true;
      sendMarkUsedRequest(id);
    }

    const onTransition = function (e) {
      if (e.propertyName === 'transform' || e.propertyName === 'opacity') {
        row.removeEventListener('transitionend', onTransition);
        finish();
      }
    };

    row.addEventListener('transitionend', onTransition);
    setTimeout(finish, 400);
  }

  function attachHandlers() {
    let touchStartX = 0;
    let touchStartY = 0;
    const threshold = 40; // px needed to consider it a swipe

    function onTouchStart(e) {
      const t = e.touches[0];
      touchStartX = t.clientX;
      touchStartY = t.clientY;
      this.classList.add('swiping');
    }

    function onTouchEnd(e) {
      this.classList.remove('swiping');
      const touch = e.changedTouches ? e.changedTouches[0] : null;
      if (!touch) return;
      const dx = touch.clientX - touchStartX;
      const dy = Math.abs(touchStartY - touch.clientY);
      // horizontal right swipe and not much vertical movement
      if (dx > threshold && dy < 80) {
        markUsedWithAnimation(this);
      }
    }

    function onClick(e) {
      // normal click/tap should also mark used (animate first)
      markUsedWithAnimation(this);
    }

    document.querySelectorAll('.swipe-row').forEach(function (row) {
      row.addEventListener('touchstart', onTouchStart, { passive: true });
      row.addEventListener('touchend', onTouchEnd, { passive: true });
      row.addEventListener('click', onClick);
    });
  }

  // Attach after DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachHandlers);
  } else {
    attachHandlers();
  }

})();
