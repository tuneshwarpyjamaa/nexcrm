// =============================================
// NexCRM — Deals
// =============================================

const STAGES = ['Lead','Meeting','Proposal','Negotiation','Won','Lost'];
let currentView = 'kanban';
let editingDealId = null;

function setView(v) {
  currentView = v;
  document.getElementById('kanbanView').style.display = v === 'kanban' ? 'flex' : 'none';
  document.getElementById('listView').style.display = v === 'list' ? 'block' : 'none';
  document.getElementById('viewKanban').classList.toggle('active', v === 'kanban');
  document.getElementById('viewList').classList.toggle('active', v === 'list');
  renderDeals();
}

async function renderDeals() {
  const deals = await DB.getDeals();
  const contacts = await DB.getContacts();

  // Summary bar
  const active = deals.filter(d => d.stage !== 'Won' && d.stage !== 'Lost');
  const won = deals.filter(d => d.stage === 'Won');
  const totalPipeline = active.reduce((s,d) => s + parseFloat(d.value||0), 0);
  const wonVal = won.reduce((s,d) => s + parseFloat(d.value||0), 0);
  const weighted = active.reduce((s,d) => s + parseFloat(d.value||0) * (parseFloat(d.probability||0)/100), 0);

  document.getElementById('pipelineSummary').innerHTML = [
    { label: 'Total Pipeline', value: formatMoney(totalPipeline), color: 'var(--accent)' },
    { label: 'Weighted Pipeline', value: formatMoney(weighted), color: 'var(--purple)' },
    { label: 'Won Revenue', value: formatMoney(wonVal), color: 'var(--green)' },
    { label: 'Active Deals', value: active.length, color: 'var(--yellow)' },
    { label: 'Win Rate', value: deals.length > 0 ? Math.round((won.length / Math.max(won.length + deals.filter(d=>d.stage==='Lost').length, 1)) * 100) + '%' : '—', color: 'var(--text)' },
  ].map(m => `
    <div class="summary-card">
      <div class="summary-label">${m.label}</div>
      <div class="summary-value" style="color:${m.color}">${m.value}</div>
    </div>
  `).join('');

  if (currentView === 'kanban') await renderKanban(deals, contacts);
  else await renderList(deals, contacts);
}

async function renderKanban(deals, contacts) {
  const board = document.getElementById('kanbanView');
  board.innerHTML = STAGES.map(stage => {
    const stageDeal = deals.filter(d => d.stage === stage);
    const stageVal = stageDeal.reduce((s,d) => s + parseFloat(d.value||0), 0);
    return `
      <div class="kanban-col" data-stage="${stage}"
           ondragover="handleDragOver(event)" ondragenter="handleDragEnter(event)"
           ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)">
        <div class="kanban-col-header">
          <span class="kanban-col-title" style="color:${STAGE_COLORS[stage]}">${stage}</span>
          <div style="display:flex;align-items:center;gap:6px">
            <span style="font-size:11.5px;color:var(--text-3);font-family:var(--mono)">${formatMoney(stageVal)}</span>
            <span class="kanban-count">${stageDeal.length}</span>
          </div>
        </div>
        ${stageDeal.map(d => {
          const c = contacts.find(c => c.id === d.contactId);
          return `
            <div class="kanban-card" draggable="true" data-deal-id="${d.id}"
                 ondragstart="handleDragStart(event)" ondragend="handleDragEnd(event)"
                 onclick="showDeal('${d.id}')">
              <div class="kanban-card-title">${d.title}</div>
              <div class="kanban-card-company">${d.company || (c ? c.company : '') || '—'}</div>
              <div class="kanban-card-footer">
                <span class="kanban-card-value">${formatMoney(d.value)}</span>
                ${d.probability ? `<span style="font-size:11.5px;color:var(--text-3)">${d.probability}%</span>` : ''}
                ${d.closeDate ? `<span style="font-size:11px;color:var(--text-3)">${formatDate(d.closeDate)}</span>` : ''}
              </div>
            </div>
          `;
        }).join('')}
        <button class="add-deal-btn" onclick="openAddDealInStage('${stage}')">+ Add Deal</button>
      </div>
    `;
  }).join('');
}

// =============================================
// Drag & Drop Handlers
// =============================================
let draggedDealId = null;
let draggedCard = null;

function handleDragStart(e) {
  draggedDealId = e.currentTarget.dataset.dealId;
  draggedCard = e.currentTarget;
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/plain', draggedDealId);
  // Delay adding the class so the drag image captures the card before it fades
  requestAnimationFrame(() => {
    draggedCard.classList.add('dragging');
  });
}

function handleDragEnd(e) {
  if (draggedCard) draggedCard.classList.remove('dragging');
  // Clean up all columns
  document.querySelectorAll('.kanban-col').forEach(col => {
    col.classList.remove('drag-over');
  });
  document.querySelectorAll('.kanban-drop-placeholder').forEach(p => p.remove());
  draggedDealId = null;
  draggedCard = null;
}

function handleDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
}

function handleDragEnter(e) {
  e.preventDefault();
  const col = e.target.closest('.kanban-col');
  if (!col) return;
  // Only highlight if it's a different column
  const sourceStage = draggedCard?.closest('.kanban-col')?.dataset.stage;
  if (col.dataset.stage !== sourceStage) {
    col.classList.add('drag-over');
  }
  // Add placeholder if not already present
  if (!col.querySelector('.kanban-drop-placeholder')) {
    const placeholder = document.createElement('div');
    placeholder.className = 'kanban-drop-placeholder';
    const addBtn = col.querySelector('.add-deal-btn');
    if (addBtn) col.insertBefore(placeholder, addBtn);
    else col.appendChild(placeholder);
  }
}

function handleDragLeave(e) {
  const col = e.target.closest('.kanban-col');
  if (!col) return;
  // Only remove if we're actually leaving the column
  const related = e.relatedTarget?.closest('.kanban-col');
  if (related !== col) {
    col.classList.remove('drag-over');
    const placeholder = col.querySelector('.kanban-drop-placeholder');
    if (placeholder) placeholder.remove();
  }
}

async function handleDrop(e) {
  e.preventDefault();
  const col = e.target.closest('.kanban-col');
  if (!col || !draggedDealId) return;
  const newStage = col.dataset.stage;
  const sourceStage = draggedCard?.closest('.kanban-col')?.dataset.stage;

  // Clean up visuals
  col.classList.remove('drag-over');
  document.querySelectorAll('.kanban-drop-placeholder').forEach(p => p.remove());

  // Only update if moved to a different stage
  if (newStage && newStage !== sourceStage) {
    await DB.updateDeal(draggedDealId, { stage: newStage });
    await DB.addActivity('deal', `Deal moved to <strong>${newStage}</strong>`, newStage === 'Won' ? 'green' : 'yellow');
    toast(`Moved to ${newStage}`, 'success');
    renderDeals();
  }
}

async function renderList(deals, contacts) {
  const q = (document.getElementById('dealFilter')?.value || '').toLowerCase();
  const sf = document.getElementById('stageFilter')?.value || '';
  let filtered = deals;
  if (q) filtered = filtered.filter(d => d.title.toLowerCase().includes(q) || (d.company||'').toLowerCase().includes(q));
  if (sf) filtered = filtered.filter(d => d.stage === sf);

  if (filtered.length === 0) {
    document.getElementById('dealsTable').innerHTML = `<tr><td colspan="8" style="text-align:center;padding:40px;color:var(--text-3)">No deals found. <a href="#" onclick="openAddDeal()" style="color:var(--accent)">Add your first deal →</a></td></tr>`;
    return;
  }

  document.getElementById('dealsTable').innerHTML = filtered.map(d => {
    const c = contacts.find(c => c.id === d.contactId);
    return `
      <tr onclick="showDeal('${d.id}')">
        <td class="cell-title"><div class="deal-title">${d.title}</div></td>
        <td class="cell-company">${d.company || '—'}</td>
        <td><span class="money">${formatMoney(d.value)}</span></td>
        <td>${stageTag(d.stage)}</td>
        <td>
          <div class="prob-wrap">
            <div class="prob-track"><div class="prob-fill" style="width:${d.probability||0}%"></div></div>
            <span class="muted">${d.probability||0}%</span>
          </div>
        </td>
        <td><span class="muted">${formatDate(d.closeDate)}</span></td>
        <td>${c ? `<div class="contact-mini">${avatarHTML(c.name,22)}<span class="contact-mini-name">${c.name}</span></div>` : '—'}</td>
        <td class="cell-actions" onclick="event.stopPropagation()">
          <div class="row-actions">
            <button class="btn-icon" onclick="openEditDeal('${d.id}')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>
            <button class="btn-icon" onclick="deleteDeal('${d.id}')" style="color:var(--red)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3,6 5,6 21,6"/><path d="M19,6l-1,14a2 2 0 0 1-2,2H8a2 2 0 0 1-2-2L5,6"/></svg></button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

async function populateContactsDropdown() {
  const contacts = await DB.getContacts();
  const sel = document.getElementById('d_contact');
  sel.innerHTML = '<option value="">No contact linked</option>' +
    contacts.map(c => `<option value="${c.id}">${c.name}${c.company ? ' ('+c.company+')' : ''}</option>`).join('');
}

async function openAddDeal() {
  editingDealId = null;
  document.getElementById('dealModalTitle').textContent = 'Add Deal';
  ['title','company','value','prob','notes'].forEach(f => document.getElementById('d_'+f).value = '');
  document.getElementById('d_stage').value = 'Lead';
  document.getElementById('d_close').value = '';
  document.getElementById('d_source').value = '';
  await populateContactsDropdown();
  openModal('dealModal');
  setTimeout(() => document.getElementById('d_title').focus(), 100);
}

function openAddDealInStage(stage) {
  openAddDeal();
  document.getElementById('d_stage').value = stage;
}

async function openEditDeal(id) {
  const d = await DB.getDeal(id);
  if (!d) return;
  editingDealId = id;
  document.getElementById('dealModalTitle').textContent = 'Edit Deal';
  document.getElementById('d_title').value = d.title || '';
  document.getElementById('d_company').value = d.company || '';
  document.getElementById('d_value').value = d.value || '';
  document.getElementById('d_stage').value = d.stage || 'Lead';
  document.getElementById('d_prob').value = d.probability || '';
  document.getElementById('d_close').value = d.closeDate || '';
  document.getElementById('d_source').value = d.source || '';
  document.getElementById('d_notes').value = d.notes || '';
  await populateContactsDropdown();
  document.getElementById('d_contact').value = d.contactId || '';
  openModal('dealModal');
}

function editCurrentDeal() {
  const id = document.getElementById('dEditBtn').dataset.id;
  if (id) { closeDetail(); openEditDeal(id); }
}

async function saveDeal() {
  const title = document.getElementById('d_title').value.trim();
  if (!title) { toast('Deal title is required', 'error'); return; }

  const data = {
    title,
    company: document.getElementById('d_company').value.trim(),
    contactId: document.getElementById('d_contact').value || null,
    value: parseFloat(document.getElementById('d_value').value) || 0,
    stage: document.getElementById('d_stage').value,
    probability: parseInt(document.getElementById('d_prob').value) || 0,
    closeDate: document.getElementById('d_close').value,
    source: document.getElementById('d_source').value,
    notes: document.getElementById('d_notes').value.trim(),
  };

  if (editingDealId) {
    await DB.updateDeal(editingDealId, data);
    toast('Deal updated', 'success');
  } else {
    await DB.addDeal(data);
    toast('Deal added', 'success');
  }

  closeModal();
  renderDeals();
}

async function deleteDeal(id) {
  if (!confirm('Delete this deal?')) return;
  await DB.deleteDeal(id);
  toast('Deal deleted');
  closeDetail();
  renderDeals();
}

async function showDeal(id) {
  const d = await DB.getDeal(id);
  if (!d) return;
  const c = d.contactId ? await DB.getContact(d.contactId) : null;

  document.getElementById('dDetailName').textContent = d.title;
  document.getElementById('dDetailStage').innerHTML = stageTag(d.stage);
  document.getElementById('dEditBtn').dataset.id = id;

  document.getElementById('dDetailBody').innerHTML = `
    <div class="detail-section">
      <div class="detail-section-title">Deal Info</div>
      <div class="detail-field"><span class="detail-field-label">Value</span><span class="detail-field-value" style="font-size:22px;font-weight:600;color:var(--green);font-family:var(--mono)">${formatMoney(d.value)}</span></div>
      <div class="detail-field"><span class="detail-field-label">Stage</span><span class="detail-field-value">${stageTag(d.stage)}</span></div>
      <div class="detail-field"><span class="detail-field-label">Probability</span>
        <div style="display:flex;align-items:center;gap:8px">
          <div style="width:100px;height:8px;background:var(--bg);border-radius:4px;overflow:hidden">
            <div style="width:${d.probability||0}%;height:100%;background:var(--accent);border-radius:4px"></div>
          </div>
          <span style="font-size:13px;font-weight:500">${d.probability||0}%</span>
        </div>
      </div>
      <div class="detail-field"><span class="detail-field-label">Weighted</span><span class="detail-field-value" style="font-weight:600;font-family:var(--mono)">${formatMoney((d.value||0) * ((d.probability||0)/100))}</span></div>
      <div class="detail-field"><span class="detail-field-label">Company</span><span class="detail-field-value">${d.company || '—'}</span></div>
      <div class="detail-field"><span class="detail-field-label">Close Date</span><span class="detail-field-value">${formatDate(d.closeDate)}</span></div>
      <div class="detail-field"><span class="detail-field-label">Source</span><span class="detail-field-value">${d.source || '—'}</span></div>
      <div class="detail-field"><span class="detail-field-label">Created</span><span class="detail-field-value">${formatDate(d.createdAt)}</span></div>
    </div>

    ${c ? `<div class="detail-section">
      <div class="detail-section-title">Contact</div>
      <div style="display:flex;align-items:center;gap:10px;padding:8px;background:var(--bg);border-radius:var(--radius-sm)">
        ${avatarHTML(c.name)}
        <div>
          <div style="font-size:14px;font-weight:500">${c.name}</div>
          <div style="font-size:12px;color:var(--text-3)">${c.company||''} ${c.email ? '· '+c.email : ''}</div>
        </div>
      </div>
    </div>` : ''}

    ${d.notes ? `<div class="detail-section"><div class="detail-section-title">Notes</div><p style="font-size:13.5px;color:var(--text-2);line-height:1.5">${d.notes}</p></div>` : ''}

    <div class="detail-section">
      <div class="detail-section-title">Move Stage</div>
      <div style="display:flex;gap:6px;flex-wrap:wrap">
        ${STAGES.map(s => `<button onclick="moveDeal('${id}','${s}')" style="padding:6px 12px;border-radius:20px;border:1px solid ${STAGE_COLORS[s]};background:${d.stage===s?STAGE_COLORS[s]:'transparent'};color:${d.stage===s?'#fff':STAGE_COLORS[s]};font-size:12px;cursor:pointer;font-family:var(--font);transition:all 0.15s">${s}</button>`).join('')}
      </div>
    </div>

    <div class="detail-section" style="border-bottom:none">
      <div class="detail-section-title">Actions</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn-secondary" style="font-size:13px;padding:7px 12px" onclick="closeDetail();openEditDeal('${id}')">✏️ Edit</button>
        <button class="btn-danger" style="font-size:13px" onclick="deleteDeal('${id}')">Delete</button>
      </div>
    </div>
  `;
  openDetail('dealDetail');
}

async function moveDeal(id, stage) {
  await DB.updateDeal(id, { stage });
  await DB.addActivity('deal', `Deal moved to <strong>${stage}</strong>`, stage === 'Won' ? 'green' : 'yellow');
  toast(`Moved to ${stage}`, 'success');
  closeDetail();
  renderDeals();
}

async function exportDeals() {
  const deals = await DB.getDeals();
  exportCSV(deals.map(d => ({
    Title: d.title, Company: d.company, Value: d.value,
    Stage: d.stage, Probability: d.probability, CloseDate: d.closeDate, Source: d.source
  })), 'deals.csv');
}

if (getParam('new') === '1') setTimeout(openAddDeal, 100);

renderDeals();
