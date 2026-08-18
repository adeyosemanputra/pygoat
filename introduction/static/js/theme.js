// Apply initial theme immediately when script executes
(function applyInitialTheme() {
  if (localStorage.getItem('theme') === 'light') {
    var pagestyle = document.getElementById('pagestyle');
    if (pagestyle) {
      pagestyle.setAttribute('href', '/static/css/light.css');
    }
  }
})();

function swapStyleSheet() {
  var elem = document.getElementById('stylesheet-toggle');
  var pagestyle = document.getElementById('pagestyle');
  if (!pagestyle) return;

  if (elem && elem.classList.contains('dark')) {
    elem.classList.remove('dark');
    elem.classList.add('light');
    localStorage.setItem('theme', 'light');
    pagestyle.setAttribute('href', '/static/css/light.css');
  } else {
    if (elem) {
      elem.classList.remove('light');
      elem.classList.add('dark');
    }
    localStorage.setItem('theme', 'dark');
    pagestyle.setAttribute('href', '/static/css/dark-theme.css');
  }
}

$(document).ready(function () {
  var elem3 = document.getElementById('stylesheet-toggle');
  if (elem3 && localStorage.getItem('theme') === 'light') {
    elem3.classList.remove('dark');
    elem3.classList.add('light');
    var pagestyle = document.getElementById('pagestyle');
    if (pagestyle) {
      pagestyle.setAttribute('href', '/static/css/light.css');
    }
  }

  $(".sidebar-header").on("click", function () {
    $("#sidebar").toggleClass("active");
    $(".pg").toggleClass("active");
  });

  $(".pg").on("click", function () {
    $("#sidebar").toggleClass("active");
    $(".pg").toggleClass("active");
  });
});
