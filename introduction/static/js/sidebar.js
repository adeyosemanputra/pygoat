// Remembers whether the sidebar is collapsed and which menus are open,
// so the sidebar looks the same after navigating to another page.
// Loaded right after the sidebar markup, so the saved state is applied
// before the first paint instead of animating into place after load.
(function () {
  var SIDEBAR_STATE_KEY = 'sidebarState';

  function readSidebarState() {
    try {
      var state = JSON.parse(localStorage.getItem(SIDEBAR_STATE_KEY));
      if (state && Array.isArray(state.open)) {
        return state;
      }
    } catch (e) {
      // localStorage can be unavailable or hold bad JSON; fall back to defaults.
    }
    return { collapsed: false, open: [] };
  }

  function writeSidebarState(state) {
    try {
      localStorage.setItem(SIDEBAR_STATE_KEY, JSON.stringify(state));
    } catch (e) {
      // Not being able to save is fine; the sidebar just won't be remembered.
    }
  }

  (function restoreSidebarState() {
    var sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    var state = readSidebarState();
    if (state.collapsed) {
      sidebar.classList.add('active');
      document.querySelectorAll('.pg').forEach(function (pg) {
        pg.classList.remove('active');
      });
    }

    state.open.forEach(function (id) {
      var menu = document.getElementById(id);
      if (!menu || !sidebar.contains(menu)) return;
      menu.classList.add('show');
      sidebar.querySelectorAll('[href="#' + id + '"]').forEach(function (toggle) {
        toggle.setAttribute('aria-expanded', 'true');
      });
    });
  })();

  // jQuery and Bootstrap are loaded at the end of the page, so wire up the
  // handlers once the document has finished parsing.
  document.addEventListener('DOMContentLoaded', function () {
    function saveSidebarState() {
      writeSidebarState({
        collapsed: $('#sidebar').hasClass('active'),
        // A submenu keeps .show when its parent is closed, so only save
        // menus that are actually visible.
        open: $('#sidebar .collapse.show').filter(function () {
          return $(this).parents('.collapse').not('.show').length === 0;
        }).map(function () {
          return this.id;
        }).get()
      });
    }

    $('.sidebar-header, .pg').on('click', function () {
      $('#sidebar').toggleClass('active');
      $('.pg').toggleClass('active');
      saveSidebarState();
    });

    $('#sidebar').on('shown.bs.collapse hidden.bs.collapse', saveSidebarState);
  });
})();
