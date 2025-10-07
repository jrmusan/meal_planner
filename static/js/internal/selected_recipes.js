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

  // Send the POST to mark ingredient used (no reload on success)
  function sendMarkUsedRequest(ingredientId) {
    if (!ingredientId) return Promise.reject(new Error('no id'));
    console.log('marking used', ingredientId);
    return new Promise(function (resolve, reject) {
      $.ajax({
        type: 'POST',
        url: '/update-ingredient/' + ingredientId,
        success: function () { resolve(); },
        error: function (xhr, status, err) { reject(err || status); }
      });
    });
  }

  function showToast(message, timeout = 4000) {
    try {
      const id = 'toast-network-error';
      let root = document.getElementById(id);
      if (root) root.remove();
      root = document.createElement('div');
      root.id = id;
      root.style.position = 'fixed';
      root.style.left = '50%';
      root.style.bottom = '24px';
      root.style.transform = 'translateX(-50%)';
      root.style.background = 'rgba(0,0,0,0.85)';
      root.style.color = 'white';
      root.style.padding = '10px 14px';
      root.style.borderRadius = '6px';
      root.style.zIndex = 9999;
      root.style.fontSize = '14px';
      root.textContent = message;
      document.body.appendChild(root);
      setTimeout(function () {
        try { root.remove(); } catch (e) {}
      }, timeout);
    } catch (e) {
      console.error('toast failed', e);
    }
  }

  // Optimistic remove: animate, remove from DOM, send request; on error reinsert & toast
  function markUsedWithAnimation(row) {
    if (!row || row.dataset._animating) return;
    row.dataset._animating = '1';
    const id = row.getAttribute('data-ingredient-id');

    // Keep a reference to the node and its parent for potential rollback
    const parent = row.parentNode;
    const nextSibling = row.nextSibling;

    // Start animation
    row.classList.add('removed');

    // After animation completes (or fallback), remove the row from DOM and then send request
    let cleanedUp = false;
    function cleanupAndSend() {
      if (cleanedUp) return; cleanedUp = true;

      // Remove row from DOM but keep the object in memory for rollback
      try { parent.removeChild(row); } catch (e) { /* ignore */ }

      sendMarkUsedRequest(id).then(function () {
        // success: nothing else to do; the UI already removed the item optimistically
      }).catch(function (err) {
        // rollback: reinsert the row back to its original location and show toast
        try {
          if (nextSibling && nextSibling.parentNode === parent) {
            parent.insertBefore(row, nextSibling);
          } else {
            parent.appendChild(row);
          }
          row.classList.remove('removed');
          delete row.dataset._animating;
        } catch (e) {
          console.error('rollback failed', e);
        }
        showToast('Network error: failed to mark ingredient. It has been restored.');
      });
    }

    // Wait for transitionend or fallback
    function onTransition(e) {
      if (e.propertyName === 'transform' || e.propertyName === 'opacity') {
        row.removeEventListener('transitionend', onTransition);
        cleanupAndSend();
      }
    }
    row.addEventListener('transitionend', onTransition);
    setTimeout(cleanupAndSend, 450);
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
