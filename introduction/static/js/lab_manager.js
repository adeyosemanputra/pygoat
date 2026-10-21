function setLabIndicatorState(button, isRunning) {
  const indicator = button.querySelector('.lab-status-indicator');
  if (!indicator) return;
  indicator.classList.toggle('running', isRunning);
  indicator.classList.toggle('not-running', !isRunning);
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function updateLabStatus() {
  const buttons = document.querySelectorAll('.lab-button[data-lab]');
  if (!buttons.length) return;

  if (typeof isAuthenticated !== 'undefined' && !isAuthenticated) {
    buttons.forEach(btn => setLabIndicatorState(btn, false));
    return;
  }

  const runningLabs = new Set();
  try {
    const response = await fetch('/challenge/list-labs/');
    const data = await response.json();
    if (data.status === 'success') {
      (data.labs || []).forEach(lab => {
        const nameParts = lab.name.split('-');
        const labName = nameParts.slice(2).join('-');
        if (labName) runningLabs.add(labName);
      });
    }
  } catch (e) {
    // ignore errors, keep default state
  }

  buttons.forEach(btn => {
    const labName = btn.getAttribute('data-lab');
    setLabIndicatorState(btn, runningLabs.has(labName));
  });
}

document.addEventListener('DOMContentLoaded', () => {
  updateLabStatus();
  loadSidebarCustomLabs();
});

function applyModalTheme(modalElement) {
  if (!modalElement) return;
  const isDark = localStorage.getItem('theme') === 'dark' || localStorage.getItem('theme') === null;

  if (isDark) {
    modalElement.className = 'modal fade modal-dark';
  } else {
    modalElement.className = 'modal fade modal-light';
  }
}

function renderManageLabList(labs, labList) {
  labList.innerHTML = '';
  labs.forEach(lab => {
    const nameParts = (lab.name || '').split('-');
    const labName = nameParts.slice(2).join('-');

    const row = document.createElement('div');
    row.className = 'd-flex justify-content-between align-items-center border rounded p-2 mb-2';

    const info = document.createElement('div');

    const strong = document.createElement('strong');
    strong.textContent = labName;

    const status = document.createElement('small');
    status.className = 'text-muted';
    status.textContent = `(${lab.status})`;

    info.appendChild(strong);
    info.appendChild(document.createTextNode(' '));
    info.appendChild(status);

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn btn-sm btn-outline-danger';
    button.textContent = 'Stop';
    button.addEventListener('click', () => stopLab(labName));

    row.appendChild(info);
    row.appendChild(button);
    labList.appendChild(row);
  });
}

async function launchLab(imageName) {
  const statusMsg = document.getElementById('launch-status-msg');
  const statusSpinner = document.getElementById('launch-status-spinner');
  const modal = $('#launchStatusModal');
  const closeBtn = document.getElementById('launch-modal-close-btn');
  const modalTitle = document.getElementById('launchStatusModalLabel');
  const modalElement = document.getElementById('launchStatusModal');
  modalTitle.innerText = 'Lab Status';

  applyModalTheme(modalElement);

  modal.modal('show');
  statusSpinner.style.display = 'inline-block';
  statusMsg.innerText = "Provisioning your lab... (this may take a while)";
  statusMsg.className = "mt-3 text-info";
  closeBtn.style.display = 'none';

  if (typeof isAuthenticated !== 'undefined' && !isAuthenticated) {
    statusSpinner.style.display = 'none';
    statusMsg.innerText = "You must be logged in to start labs. Please log in first.";
    statusMsg.className = "mt-3 text-danger";
    closeBtn.style.display = 'inline-block';
    return;
  }

  try {
    const response = await fetch(`/challenge/start-lab/${imageName}/`);

    if (response.status === 401) {
      statusSpinner.style.display = 'none';
      statusMsg.innerText = "You are not authenticated. Please log in to start labs.";
      statusMsg.className = "mt-3 text-danger";
      closeBtn.style.display = 'inline-block';
      return;
    }

    if (!response.ok) {
      statusSpinner.style.display = 'none';
      let errMsg = `Request failed with status ${response.status}.`;
      if (response.status === 403) errMsg = "Forbidden: you don't have permission to start this lab (403).";
      else if (response.status === 404) errMsg = "Lab not found (404).";
      else if (response.status === 429) errMsg = "Too many requests. Please try again later (429).";
      else if (response.status >= 500) errMsg = "Server error. Please try again later.";

      try {
        const maybeJson = await response.json();
        if (maybeJson && maybeJson.message) errMsg = maybeJson.message;
      } catch (e) {
        // ignore JSON parse errors
      }

      statusMsg.innerText = "Error: " + errMsg;
      statusMsg.className = "mt-3 text-danger";
      closeBtn.style.display = 'inline-block';
      return;
    }

    let data = {};
    if (response.headers.get('content-type') && response.headers.get('content-type').includes('application/json')) {
      data = await response.json();
    }

    statusSpinner.style.display = 'none';

    if (data.status === 'ready' || data.status === 'created') {
      // Validate URL scheme to prevent javascript: or data: XSS vectors
      const labUrl = (typeof data.url === 'string' && /^https?:\/\//i.test(data.url)) ? data.url : null;

      const labWindow = labUrl ? window.open(labUrl) : null;

      statusMsg.textContent = '';
      statusMsg.className = "mt-3 text-success";

      if (labWindow) {
        const heading = document.createTextNode('Lab Ready! Opening in new tab... ');
        const br = document.createElement('br');
        const detail = document.createElement('small');
        detail.className = 'text-success';
        detail.textContent = '✓ Lab opened successfully';
        statusMsg.appendChild(heading);
        statusMsg.appendChild(br);
        statusMsg.appendChild(detail);
        modalTitle.innerText = 'Lab Status';
      } else if (labUrl) {
        const heading = document.createTextNode('Lab Ready! ');
        const br1 = document.createElement('br');
        const warning = document.createElement('small');
        warning.className = 'text-warning';
        warning.textContent = '⚠ Unable to redirect to the lab';
        const br2 = document.createElement('br');
        const link = document.createElement('a');
        link.href = labUrl;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.className = 'btn btn-primary btn-sm mt-2';
        const icon = document.createElement('i');
        icon.className = 'fas fa-external-link-alt';
        link.appendChild(icon);
        link.appendChild(document.createTextNode(' Open this lab in a new tab'));
        statusMsg.appendChild(heading);
        statusMsg.appendChild(br1);
        statusMsg.appendChild(warning);
        statusMsg.appendChild(br2);
        statusMsg.appendChild(link);
      } else {
        statusMsg.textContent = 'Lab started but returned an invalid URL.';
        statusMsg.className = "mt-3 text-danger";
        closeBtn.style.display = 'inline-block';
      }
      updateLabStatus();
    } else {
      const msg = data && data.message ? data.message : 'Failed to start lab.';
      statusMsg.textContent = "Error: " + msg;
      statusMsg.className = "mt-3 text-danger";
      closeBtn.style.display = 'inline-block';
    }
  } catch (error) {
    console.error(error);
    statusSpinner.style.display = 'none';
    if (error instanceof TypeError) {
      statusMsg.innerText = "Network error: unable to reach server. Check your connection.";
    } else {
      statusMsg.innerText = `Unexpected error: ${error && error.message ? error.message : error}`;
    }
    statusMsg.className = "mt-3 text-danger";
    closeBtn.style.display = 'inline-block';
  }
}

async function manageLabs() {
  const manageBtn = document.getElementById('manage-labs-btn');
  const originalText = manageBtn.innerText;
  const statusMsg = document.getElementById('manage-status-msg');
  const statusSpinner = document.getElementById('manage-status-spinner');
  const modal = $('#manageStatusModal');
  const closeBtn = document.getElementById('manage-modal-close-btn');
  const modalTitle = document.getElementById('manageStatusModalLabel');
  const labList = document.getElementById('manage-lab-list');
  const modalStopAllBtn = document.getElementById('manage-modal-stop-all-btn');
  const modalElement = document.getElementById('manageStatusModal');

  applyModalTheme(modalElement);
  modalTitle.innerText = "Manage Labs";
  modal.modal('show');
  statusSpinner.style.display = 'inline-block';
  statusMsg.innerText = "Fetching running labs...";
  statusMsg.className = "mt-3 text-info";
  closeBtn.style.display = 'none';
  labList.innerHTML = '';
  modalStopAllBtn.style.display = 'none';
  manageBtn.innerText = "Loading...";
  manageBtn.disabled = true;

  try {
    const csrftoken = getCookie('csrftoken');
    const listResponse = await fetch('/challenge/list-labs/');
    const listData = await listResponse.json();
    statusSpinner.style.display = 'none';

    if (listData.status === 'success') {
      const labs = listData.labs || [];
      if (labs.length === 0) {
        statusMsg.innerText = "No running labs found.";
        statusMsg.className = "mt-3 text-info";
        closeBtn.style.display = 'inline-block';
      } else {
        statusMsg.innerText = "Select a lab to stop or stop all.";
        statusMsg.className = "mt-3 text-info";
        renderManageLabList(labs, labList);
        modalStopAllBtn.style.display = 'inline-block';
        modalStopAllBtn.onclick = async () => {
          statusSpinner.style.display = 'inline-block';
          statusMsg.innerText = "Stopping all running labs...";
          statusMsg.className = "mt-3 text-info";
          modalStopAllBtn.disabled = true;
          const response = await fetch('/challenge/stop-labs/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            }
          });
          const data = await response.json();
          statusSpinner.style.display = 'none';
          modalStopAllBtn.disabled = false;
          if (data.status === 'success') {
            statusMsg.innerText = data.message;
            statusMsg.className = "mt-3 text-success";
            labList.innerHTML = '';
            modalStopAllBtn.style.display = 'none';
            updateLabStatus();
            setTimeout(() => {
              manageBtn.innerText = originalText;
              manageBtn.disabled = false;
              modalTitle.innerText = 'Manage Labs';
            }, 10000);
          } else {
            statusMsg.innerText = `Error: ${data.message}`;
            statusMsg.className = "mt-3 text-danger";
            closeBtn.style.display = 'inline-block';
          }
        };
        closeBtn.style.display = 'inline-block';
      }
    } else {
      statusMsg.innerText = `Error: ${listData.message}`;
      statusMsg.className = "mt-3 text-danger";
      closeBtn.style.display = 'inline-block';
    }
    manageBtn.innerText = originalText;
    manageBtn.disabled = false;
  } catch (error) {
    console.error(error);
    statusSpinner.style.display = 'none';
    statusMsg.innerText = "Failed to load labs. Check console for details.";
    statusMsg.className = "mt-3 text-danger";
    manageBtn.innerText = originalText;
    manageBtn.disabled = false;
    closeBtn.style.display = 'inline-block';
  }
}

async function stopLab(labName) {
  const statusMsg = document.getElementById('manage-status-msg');
  const statusSpinner = document.getElementById('manage-status-spinner');
  const labList = document.getElementById('manage-lab-list');
  const modalStopAllBtn = document.getElementById('manage-modal-stop-all-btn');

  try {
    statusMsg.innerText = `Stopping ${labName}...`;
    statusMsg.className = "mt-3 text-info";
    statusSpinner.style.display = 'inline-block';
    const csrftoken = getCookie('csrftoken');
    const response = await fetch(`/challenge/stop-lab/${labName}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }
    });
    const data = await response.json();
    statusSpinner.style.display = 'none';
    if (data.status === 'success') {
      statusMsg.innerText = data.message;
      statusMsg.className = "mt-3 text-success";
      const listResponse = await fetch('/challenge/list-labs/');
      const listData = await listResponse.json();
      if (listData.status === 'success' && listData.labs.length > 0) {
        renderManageLabList(listData.labs, labList);
        modalStopAllBtn.style.display = 'inline-block';
      } else {
        labList.innerHTML = '';
        modalStopAllBtn.style.display = 'none';
      }
      updateLabStatus();
    } else {
      statusMsg.innerText = `Error: ${data.message}`;
      statusMsg.className = "mt-3 text-danger";
    }
  } catch (error) {
    console.error(error);
    statusSpinner.style.display = 'none';
    statusMsg.innerText = "Failed to stop lab. Check console for details.";
    statusMsg.className = "mt-3 text-danger";
  }
}

async function openCustomLabsModal() {
  const modal = $('#customLabsModal');
  const modalElement = document.getElementById('customLabsModal');
  applyModalTheme(modalElement);
  modal.modal('show');
  resetCustomLabForm();
  await fetchAndRenderCustomLabs();
}

async function fetchAndRenderCustomLabs() {
  const spinner = document.getElementById('custom-labs-spinner');
  const tableBody = document.getElementById('custom-labs-table-body');
  const noLabsMsg = document.getElementById('no-custom-labs-msg');

  spinner.style.display = 'block';
  tableBody.innerHTML = '';
  noLabsMsg.style.display = 'none';

  try {
    const response = await fetch('/challenge/custom-labs/list/');
    const data = await response.json();
    spinner.style.display = 'none';

    if (data.status === 'success') {
      const labs = data.labs || [];
      if (labs.length === 0) {
        noLabsMsg.style.display = 'block';
      } else {
        labs.forEach(lab => {
          const tr = document.createElement('tr');

          const tdName = document.createElement('td');
          tdName.textContent = lab.name;

          const tdLoc = document.createElement('td');
          tdLoc.textContent = lab.build_location;

          const tdPort = document.createElement('td');
          tdPort.textContent = lab.port;

          const tdActions = document.createElement('td');

          const btnEdit = document.createElement('button');
          btnEdit.type = 'button';
          btnEdit.className = 'btn btn-sm btn-outline-primary mr-1';
          btnEdit.textContent = 'Edit';
          btnEdit.addEventListener('click', () => editCustomLab(lab.id, lab.name, lab.build_location, lab.port));

          const btnDelete = document.createElement('button');
          btnDelete.type = 'button';
          btnDelete.className = 'btn btn-sm btn-outline-danger';
          btnDelete.textContent = 'Remove';
          btnDelete.addEventListener('click', () => deleteCustomLab(lab.id));

          tdActions.appendChild(btnEdit);
          tdActions.appendChild(btnDelete);

          tr.appendChild(tdName);
          tr.appendChild(tdLoc);
          tr.appendChild(tdPort);
          tr.appendChild(tdActions);

          tableBody.appendChild(tr);
        });
      }
    } else {
      showCustomLabsAlert(`Error listing labs: ${data.message}`, 'danger');
    }
  } catch (e) {
    spinner.style.display = 'none';
    showCustomLabsAlert(`Error listing labs: ${e.message || e}`, 'danger');
  }
}

function editCustomLab(id, name, buildLocation, port) {
  document.getElementById('custom-lab-id').value = id;
  document.getElementById('custom-lab-name').value = name;
  document.getElementById('custom-lab-build-location').value = buildLocation;
  document.getElementById('custom-lab-port').value = port;

  document.getElementById('custom-lab-form-title').textContent = 'Edit Custom Lab';
  document.getElementById('custom-lab-submit-btn').textContent = 'Update Lab';
  document.getElementById('custom-lab-cancel-btn').style.display = 'inline-block';
}

function resetCustomLabForm() {
  document.getElementById('custom-lab-id').value = '';
  document.getElementById('custom-lab-form').reset();
  document.getElementById('custom-lab-form-title').textContent = 'Add New Custom Lab';
  document.getElementById('custom-lab-submit-btn').textContent = 'Add Lab';
  document.getElementById('custom-lab-cancel-btn').style.display = 'none';
}

function showCustomLabsAlert(message, type) {
  const alertDiv = document.getElementById('custom-labs-alert');
  const alertMsg = document.getElementById('custom-labs-alert-msg');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertMsg.textContent = message;
  alertDiv.classList.remove('d-none');
  setTimeout(() => {
    alertDiv.classList.add('d-none');
  }, 5000);
}

async function deleteCustomLab(id) {
  if (!confirm('Are you sure you want to remove this lab?')) return;
  const csrftoken = getCookie('csrftoken');
  try {
    const response = await fetch(`/challenge/custom-labs/delete/${id}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }
    });
    const data = await response.json();
    if (data.status === 'success') {
      showCustomLabsAlert(data.message, 'success');
      await fetchAndRenderCustomLabs();
      await loadSidebarCustomLabs();
      updateLabStatus();
    } else {
      showCustomLabsAlert(`Error: ${data.message}`, 'danger');
    }
  } catch (e) {
    showCustomLabsAlert(`Error: ${e.message || e}`, 'danger');
  }
}

async function loadSidebarCustomLabs() {
  const container = document.getElementById('sidebar-custom-labs-container');
  if (!container) return;

  try {
    const response = await fetch('/challenge/custom-labs/list/');
    const data = await response.json();

    container.innerHTML = '';

    if (data.status === 'success') {
      const labs = data.labs || [];
      if (labs.length === 0) {
        const noLabs = document.createElement('small');
        noLabs.className = 'text-muted d-block p-3';
        noLabs.textContent = 'No custom labs';
        container.appendChild(noLabs);
      } else {
        labs.forEach(lab => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'sidebar-list-items lab-button';
          btn.addEventListener('click', () => launchLab(lab.name));
          btn.setAttribute('data-lab', lab.name);

          const icon = document.createElement('i');
          icon.className = 'fas fa-cog';

          const text = document.createTextNode(` ${lab.name}`);

          const indicator = document.createElement('span');
          indicator.className = 'lab-status-indicator not-running';
          indicator.setAttribute('aria-hidden', 'true');

          btn.appendChild(icon);
          btn.appendChild(text);
          btn.appendChild(indicator);
          container.appendChild(btn);
        });
      }
      // After loading custom labs, refresh running indicators
      updateLabStatus();
    }
  } catch (e) {
    console.error('Failed to load custom labs for sidebar:', e);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('custom-lab-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = document.getElementById('custom-lab-id').value;
      const name = document.getElementById('custom-lab-name').value;
      const buildLocation = document.getElementById('custom-lab-build-location').value;
      const port = document.getElementById('custom-lab-port').value;

      const payload = { name, build_location: buildLocation, port };
      const csrftoken = getCookie('csrftoken');

      let url = '/challenge/custom-labs/create/';
      if (id) {
        url = `/challenge/custom-labs/update/${id}/`;
      }

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
          },
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (data.status === 'success') {
          showCustomLabsAlert(data.message, 'success');
          resetCustomLabForm();
          await fetchAndRenderCustomLabs();
          await loadSidebarCustomLabs();
          updateLabStatus();
        } else {
          showCustomLabsAlert(`Error: ${data.message}`, 'danger');
        }
      } catch (err) {
        showCustomLabsAlert(`Error: ${err.message || err}`, 'danger');
      }
    });
  }
});
