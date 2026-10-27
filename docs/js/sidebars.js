// Collapsible left (navigation) and right (on this page) sidebars.
// Toggle with the header buttons or the [ and ] keys; state persists across pages.

(function () {
  'use strict';

  var root = document.documentElement;
  var KEYS = { left: 'dva-hide-left', right: 'dva-hide-right' };

  function stored(side) {
    try { return localStorage.getItem(KEYS[side]) === '1'; } catch (e) { return false; }
  }

  function apply(side, hidden) {
    root.classList.toggle('hide-' + side, hidden);
    var btn = document.querySelector('.sidebar-toggle--' + side);
    if (btn) {
      btn.setAttribute('aria-pressed', String(hidden));
      btn.title = (hidden ? 'Show ' : 'Hide ') + (side === 'left' ? 'navigation' : 'page contents') +
        (side === 'left' ? ' ( [ )' : ' ( ] )');
    }
  }

  function toggle(side) {
    var hidden = !root.classList.contains('hide-' + side);
    apply(side, hidden);
    try { localStorage.setItem(KEYS[side], hidden ? '1' : '0'); } catch (e) {}
  }

  apply('left', stored('left'));
  apply('right', stored('right'));

  function icon(side) {
    var bar = side === 'left' ? 9 : 15;
    return '<svg viewBox="0 0 24 24" aria-hidden="true">' +
      '<rect x="3.5" y="4.5" width="17" height="15" rx="1" style="fill:none;stroke:currentColor;stroke-width:1.5"/>' +
      '<path d="M' + bar + ' 4.5v15" style="fill:none;stroke:currentColor;stroke-width:1.5"/></svg>';
  }

  var option = document.querySelector('.md-header__option');
  if (option) {
    ['left', 'right'].forEach(function (side) {
      // Pages that hide a sidebar (e.g. the home page) get no toggle for it.
      var bar = document.querySelector('.md-sidebar--' + (side === 'left' ? 'primary' : 'secondary'));
      if (!bar || bar.hidden) return;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'md-header__button md-icon sidebar-toggle sidebar-toggle--' + side;
      btn.innerHTML = icon(side);
      btn.addEventListener('click', function () { toggle(side); });
      option.parentNode.insertBefore(btn, option);
      apply(side, root.classList.contains('hide-' + side));
    });
  }

  // Enable transitions only after the initial state has been painted.
  requestAnimationFrame(function () {
    requestAnimationFrame(function () { root.classList.add('sidebar-anim'); });
  });

  document.addEventListener('keydown', function (e) {
    var t = e.target;
    if (e.ctrlKey || e.metaKey || e.altKey || (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)))) return;
    if (e.key === '[') toggle('left');
    if (e.key === ']') toggle('right');
  });
})();
