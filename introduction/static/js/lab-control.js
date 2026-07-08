(function () {
  'use strict';

  var el = document.getElementById('lab-controls');
  if (!el) return;

  var LAB_ID = el.dataset.lab;
  if (!LAB_ID) return;

  var MAX_LABS = 3;
  if (getComputedStyle(el.parentNode).position === 'static') {
    el.parentNode.style.position = 'relative';
  }

  /* inject styles*/
  var style = document.createElement('style');
  style.textContent = [

    '#pyg-badge.badge-success {',
    '  animation: pyg-pulse 2s ease-in-out infinite;',
    '}',
    '@keyframes pyg-pulse {',
    '  0%,100% { box-shadow: 0 0 0 0 rgba(40,167,69,0.5); }',
    '  50%      { box-shadow: 0 0 0 5px rgba(40,167,69,0);  }',
    '}',
  
    '#pyg-status-wrap {',
    '  display: block;',
    '  margin-top: 5px;',
    '}',

    '#lab-controls {',
    '  position: absolute;',
    '  top: 0;',
    '  right: 0;',
    '}',

    /* start /stop buttons */
    '#pyg-start, #pyg-stop {',
    '  display: inline-flex;',
    '  align-items: center;',
    '  gap: 6px;',
    '  padding: 6px 14px;',
    '  font-size: 12.5px;',
    '  font-weight: 600;',
    '  border: none;',
    '  border-radius: 6px;',
    '  cursor: pointer;',
    '  color: #fff;',
    '  transition: opacity .2s, transform .15s, box-shadow .2s;',
    '  white-space: nowrap;',
    '}',
    '#pyg-start {',
    '  background: #16a34a;',
    '  box-shadow: 0 1px 3px rgba(22,163,74,.35);',
    '}',
    '#pyg-stop {',
    '  background: #dc2626;',
    '  box-shadow: 0 1px 3px rgba(220,38,38,.3);',
    '}',
    '#pyg-start:hover:not(:disabled), #pyg-stop:hover:not(:disabled) {',
    '  opacity: .88;',
    '  transform: translateY(-1px);',
    '}',
    '#pyg-start:disabled, #pyg-stop:disabled {',
    '  opacity: .5;',
    '  cursor: not-allowed;',
    '  transform: none;',
    '  box-shadow: none;',
    '}',

    /* Limit toast */
    '#pyg-limit-msg {',
    '  display: none;',
    '  position: absolute;',
    '  top: calc(100% + 10px);',
    '  right: 0;',
    '  z-index: 50;',
    '  min-width: 270px;',
    '  padding: 12px 14px;',
    '  background: #fff;',
    '  border: 1px solid #fecaca;',
    '  border-left: 4px solid #dc2626;',
    '  border-radius: 8px;',
    '  box-shadow: 0 4px 16px rgba(0,0,0,.10);',
    '  animation: pyg-toast-in .18s ease;',
    '}',
    '#pyg-limit-msg.show {',
    '  display: flex;',
    '  gap: 10px;',
    '  align-items: flex-start;',
    '}',
    '@keyframes pyg-toast-in {',
    '  from { opacity: 0; transform: translateY(-4px); }',
    '  to   { opacity: 1; transform: translateY(0); }',
    '}',
    '#pyg-limit-msg strong {',
    '  display: block;',
    '  font-size: 12.5px;',
    '  color: #1a1a1a;',
    '  margin-bottom: 2px;',
    '}',
    '#pyg-limit-msg span {',
    '  font-size: 11.5px;',
    '  color: #6b7280;',
    '  line-height: 1.45;',
    '}',
    '#pyg-limit-close {',
    '  margin-left: auto;',
    '  background: none;',
    '  border: none;',
    '  cursor: pointer;',
    '  color: #9ca3af;',
    '  font-size: 16px;',
    '  padding: 0 0 0 8px;',
    '  line-height: 1;',
    '  transition: color .15s;',
    '}',
    '#pyg-limit-close:hover { color: #374151; }'
  ].join('\n');
  document.head.appendChild(style);


  function getOrCreateStatusMount() {
    var explicit = document.getElementById('lab-status');
    if (explicit) return explicit;


    var sibling = el.previousElementSibling;
    while (sibling) {
      if (/^H[1-4]$/.test(sibling.tagName)) {
        var wrap = document.createElement('div');
        wrap.id = 'pyg-status-wrap';
        sibling.appendChild(wrap);
        return wrap;
      }
      sibling = sibling.previousElementSibling;
    }

    var wrap = document.createElement('div');
    wrap.id = 'pyg-status-wrap';
    el.parentNode.insertBefore(wrap, el);
    return wrap;
  }

  var statusMount = getOrCreateStatusMount();
  statusMount.innerHTML =
    '<span id="pyg-badge" class="badge badge-secondary"' +
    ' style="font-size:12px;padding:4px 10px;">' +
      '<i class="fas fa-circle" style="font-size:8px;margin-right:5px;"></i>' +
      '<span id="pyg-badge-text">Stopped</span>' +
    '</span>';

  el.innerHTML =
    '<div style="position:relative;display:inline-flex;align-items:center;">' +
      '<button id="pyg-start">' +
        '<i class="fas fa-play" style="font-size:10px;"></i> Start Lab' +
      '</button>' +
      '<button id="pyg-stop" style="display:none;margin-left:6px;">' +
        '<i class="fas fa-stop" style="font-size:10px;"></i> Stop Lab' +
      '</button>' +
      '<div id="pyg-limit-msg" role="alert">' +
        '<div>' +
          '<strong>Lab limit reached</strong>' +
          '<span>Stop an active lab to start a new one (max&nbsp;3).</span>' +
        '</div>' +
        '<button id="pyg-limit-close" aria-label="Dismiss">&times;</button>' +
      '</div>' +
    '</div>';

  var startBtn  = document.getElementById('pyg-start');
  var stopBtn   = document.getElementById('pyg-stop');
  var limitMsg  = document.getElementById('pyg-limit-msg');

  document.getElementById('pyg-limit-close').onclick = function () {
    limitMsg.classList.remove('show');
  };


  function setAccessButtons(labUrl) {
    document.querySelectorAll('a.lab-access-btn').forEach(function (a) {
      if (labUrl) {
        a.href                = labUrl + (a.dataset.path || '');
        a.style.pointerEvents = 'auto';
        a.style.opacity       = '1';
      } else {
        a.href                = '#';
        a.style.pointerEvents = 'none';
        a.style.opacity       = '0.5';
      }
    });
  }
  
  function applyRunning(labUrl) {
    limitMsg.classList.remove('show');
    var badge = document.getElementById('pyg-badge');
    badge.className = 'badge badge-success';
    document.getElementById('pyg-badge-text').textContent = 'Running';
    startBtn.style.display = 'none';
    stopBtn.style.display  = 'inline-flex';
    stopBtn.disabled       = false;
    stopBtn.innerHTML      = '<i class="fas fa-stop" style="font-size:10px;"></i> Stop Lab';
    setAccessButtons(labUrl);
    if (typeof updateLabStatus === 'function') updateLabStatus();
  }

  function applyStarting() {
    limitMsg.classList.remove('show');
    var badge = document.getElementById('pyg-badge');
    badge.className = 'badge badge-warning';
    document.getElementById('pyg-badge-text').textContent = 'Starting\u2026';
    startBtn.disabled  = true;
    startBtn.innerHTML = '<i class="fas fa-spinner fa-spin" style="font-size:10px;"></i> Starting\u2026';
    setAccessButtons(null);
  }

  function applyStopped() {
    limitMsg.classList.remove('show');
    var badge = document.getElementById('pyg-badge');
    badge.className = 'badge badge-secondary';
    document.getElementById('pyg-badge-text').textContent = 'Stopped';
    startBtn.style.display = 'inline-flex';
    startBtn.disabled      = false;
    startBtn.innerHTML     = '<i class="fas fa-play" style="font-size:10px;"></i> Start Lab';
    stopBtn.style.display  = 'none';
    setAccessButtons(null);
    if (typeof updateLabStatus === 'function') updateLabStatus();
  }

  /* fetch running labs*/
  async function getRunningLabs() {
    try {
      var res  = await fetch('/challenge/list-labs/');
      var data = await res.json();
      if (data.status !== 'success') return { count: 0, thisRunning: false, url: '' };
      var labs = data.labs || [];
      var thisLab = labs.find(function (l) {
        return l.name && l.name.endsWith('-' + LAB_ID) && l.status === 'running';
      });
      return {
        count:       labs.filter(function (l) { return l.status === 'running'; }).length,
        thisRunning: !!thisLab,
        url:         thisLab ? (thisLab.url || '') : ''
      };
    } catch (e) {
      return { count: 0, thisRunning: false, url: '' };
    }
  }

  /* start button */
  startBtn.addEventListener('click', async function () {
    var info = await getRunningLabs();
    if (info.count >= MAX_LABS) {
      limitMsg.classList.add('show');
      return;
    }
    applyStarting();
    try {
      var res  = await fetch('/challenge/start-lab/' + LAB_ID + '/');
      var data = await res.json();
      if (data.status === 'ready' || data.status === 'created') {
        applyRunning(data.url || '');
      } else {
        applyStopped();
        console.error('[PyGoat] start-lab error:', data.message);
      }
    } catch (e) {
      applyStopped();
    }
  });

  /* stop button */
  stopBtn.addEventListener('click', async function () {
    stopBtn.disabled  = true;
    stopBtn.innerHTML = '<i class="fas fa-spinner fa-spin" style="font-size:10px;"></i> Stopping\u2026';
    try {
      await fetch('/challenge/stop-lab/' + LAB_ID + '/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        }
      });
      applyStopped();
    } catch (e) {
      stopBtn.disabled  = false;
      stopBtn.innerHTML = '<i class="fas fa-stop" style="font-size:10px;"></i> Stop Lab';
    }
  });

  /*page load- reflect real container state*/
  (async function init() {
    var info = await getRunningLabs();
    if (info.thisRunning) {
      try {
        var res  = await fetch('/challenge/start-lab/' + LAB_ID + '/');
        var data = await res.json();
        applyRunning(data.url || '');
      } catch (e) {
        applyRunning('');
      }
    } else {
      applyStopped();
    }
  }());

}());