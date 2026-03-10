// =============================================
// NexCRM — Contacts
// =============================================

let editingContactId = null;

async function renderContacts() {
  const q = document.getElementById('filterInput').value.toLowerCase();
  const sf = document.getElementById('statusFilter').value;
  let contacts = await DB.getContacts();

  if (q) contacts = contacts.filter(c =>
    c.name.toLowerCase().includes(q) ||
    (c.company||'').toLowerCase().includes(q) ||
    (c.email||'').toLowerCase().includes(q) ||
    (c.phone||'').includes(q)
  );
  if (sf) contacts = contacts.filter(c => c.status === sf);

  document.getElementById('contactCount').textContent = `${contacts.length} contact${contacts.length !== 1 ? 's' : ''}`;

  if (contacts.length === 0) {
    document.getElementById('contactsTable').innerHTML = `
      <tr><td colspan="8" style="text-align:center;padding:40px;color:var(--text-3)">
        No contacts found. <a href="#" onclick="openAddContact()" style="color:var(--accent)">Add your first contact →</a>
      </td></tr>`;
    return;
  }

  document.getElementById('contactsTable').innerHTML = contacts.map(c => `
    <tr onclick="showContact('${c.id}')">
      <td>
        <div style="display:flex;align-items:center;gap:10px">
          ${avatarHTML(c.name)}
          <div>
            <div style="font-weight:500">${c.name}</div>
            ${c.title ? `<div style="font-size:12px;color:var(--text-3)">${c.title}</div>` : ''}
          </div>
        </div>
      </td>
      <td>${c.company || '—'}</td>
      <td><a href="mailto:${c.email}" onclick="event.stopPropagation()" style="color:var(--accent)">${c.email || '—'}</a></td>
      <td>${c.phone || '—'}</td>
      <td>${statusTag(c.status || 'Lead')}</td>
      <td>${(c.tags||[]).filter(Boolean).map(t => `<span class="tag tag-gray">${t}</span>`).join(' ') || '—'}</td>
      <td style="color:var(--text-3);font-size:12.5px">${formatDate(c.createdAt)}</td>
      <td onclick="event.stopPropagation()">
        <div style="display:flex;gap:4px">
          <button class="btn-icon" title="Edit" onclick="openEditContact('${c.id}')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
          <button class="btn-icon" title="Delete" onclick="deleteContact('${c.id}')" style="color:var(--red)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3,6 5,6 21,6"/><path d="M19,6l-1,14a2 2 0 0 1-2,2H8a2 2 0 0 1-2-2L5,6"/><path d="M10,11v6"/><path d="M14,11v6"/></svg>
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

function openAddContact() {
  editingContactId = null;
  document.getElementById('contactModalTitle').textContent = 'Add Contact';
  ['name','company','email','phone','title','linkedin','website','address','notes'].forEach(f => document.getElementById('c_'+f).value = '');
  document.getElementById('c_status').value = 'Lead';
  document.getElementById('c_source').value = '';
  document.getElementById('c_tags').value = '';
  openModal('contactModal');
  setTimeout(() => document.getElementById('c_name').focus(), 100);
}

async function openEditContact(id) {
  const c = await DB.getContact(id);
  if (!c) return;
  editingContactId = id;
  document.getElementById('contactModalTitle').textContent = 'Edit Contact';
  document.getElementById('c_name').value = c.name || '';
  document.getElementById('c_company').value = c.company || '';
  document.getElementById('c_email').value = c.email || '';
  document.getElementById('c_phone').value = c.phone || '';
  document.getElementById('c_title').value = c.title || '';
  document.getElementById('c_status').value = c.status || 'Lead';
  document.getElementById('c_linkedin').value = c.linkedin || '';
  document.getElementById('c_website').value = c.website || '';
  document.getElementById('c_source').value = c.source || '';
  document.getElementById('c_address').value = c.address || '';
  document.getElementById('c_notes').value = c.notes || '';
  document.getElementById('c_tags').value = (c.tags||[]).join(', ');
  openModal('contactModal');
}

function editCurrentContact() {
  const id = document.getElementById('detailEditBtn').dataset.id;
  if (id) { closeDetail(); openEditContact(id); }
}

async function saveContact() {
  const name = document.getElementById('c_name').value.trim();
  if (!name) { toast('Name is required', 'error'); return; }

  const data = {
    name,
    company: document.getElementById('c_company').value.trim(),
    email: document.getElementById('c_email').value.trim(),
    phone: document.getElementById('c_phone').value.trim(),
    title: document.getElementById('c_title').value.trim(),
    status: document.getElementById('c_status').value,
    linkedin: document.getElementById('c_linkedin').value.trim(),
    website: document.getElementById('c_website').value.trim(),
    source: document.getElementById('c_source').value,
    address: document.getElementById('c_address').value.trim(),
    notes: document.getElementById('c_notes').value.trim(),
    tags: document.getElementById('c_tags').value.split(',').map(t => t.trim()).filter(Boolean),
  };

  if (editingContactId) {
    await DB.updateContact(editingContactId, data);
    toast('Contact updated', 'success');
  } else {
    await DB.addContact(data);
    toast('Contact added', 'success');
  }

  closeModal();
  renderContacts();
}

async function deleteContact(id) {
  if (!confirm('Delete this contact? This cannot be undone.')) return;
  await DB.deleteContact(id);
  toast('Contact deleted');
  closeDetail();
  renderContacts();
}

async function showContact(id) {
  const c = await DB.getContact(id);
  if (!c) return;

  document.getElementById('detailAvatar').innerHTML = avatarHTML(c.name, 44);
  document.getElementById('detailName').textContent = c.name;
  document.getElementById('detailSub').textContent = [c.title, c.company].filter(Boolean).join(' at ') || '';
  document.getElementById('detailEditBtn').dataset.id = id;

  // Get related deals and tasks
  const deals = await DB.getDeals();
  const tasks = await DB.getTasks();
  const notes = await DB.getNotes();

  const relatedDeals = deals.filter(d => d.contactId === id);
  const relatedTasks = tasks.filter(t => t.contactId === id);
  const relatedNotes = notes.filter(n => n.contactId === id);

  document.getElementById('detailBody').innerHTML = `
    <div class="detail-section">
      <div class="detail-section-title">Contact Info</div>
      ${field('Email', c.email ? `<a href="mailto:${c.email}">${c.email}</a>` : '—')}
      ${field('Phone', c.phone ? `<a href="tel:${c.phone}">${c.phone}</a>` : '—')}
      ${field('Company', c.company || '—')}
      ${field('Title', c.title || '—')}
      ${field('Status', statusTag(c.status || 'Lead'))}
      ${field('Source', c.source || '—')}
      ${field('Address', c.address || '—')}
      ${c.linkedin ? field('LinkedIn', `<a href="${c.linkedin}" target="_blank">View Profile →</a>`) : ''}
      ${c.website ? field('Website', `<a href="${c.website}" target="_blank">${c.website}</a>`) : ''}
      ${c.tags?.length ? field('Tags', c.tags.map(t=>`<span class="tag tag-gray">${t}</span>`).join(' ')) : ''}
    </div>

    ${c.notes ? `<div class="detail-section"><div class="detail-section-title">Notes</div><p style="font-size:13.5px;color:var(--text-2);line-height:1.5">${c.notes}</p></div>` : ''}

    <div class="detail-section">
      <div class="detail-section-title">Deals (${deals.length})</div>
      ${deals.length === 0 ? '<p style="font-size:13px;color:var(--text-3)">No deals yet.</p>' :
        deals.map(d => `<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:13.5px;border-bottom:1px solid var(--border-light)">
          <span>${d.title}</span>
          <span style="color:var(--green);font-weight:600;font-family:var(--mono)">${formatMoney(d.value)}</span>
        </div>`).join('')}
      <div style="margin-top:8px"><a href="deals.html?new=1" style="font-size:12.5px;color:var(--accent)">+ Add Deal</a></div>
    </div>

    <div class="detail-section">
      <div class="detail-section-title">Tasks (${tasks.filter(t=>!t.done).length} open)</div>
      ${tasks.length === 0 ? '<p style="font-size:13px;color:var(--text-3)">No tasks yet.</p>' :
        tasks.slice(0,5).map(t => `<div style="display:flex;align-items:center;gap:8px;padding:6px 0;font-size:13.5px;border-bottom:1px solid var(--border-light)">
          <div style="width:14px;height:14px;border-radius:3px;background:${t.done?'var(--green)':'var(--border)'};flex-shrink:0"></div>
          <span style="${t.done?'text-decoration:line-through;color:var(--text-3)':''}">${t.title}</span>
        </div>`).join('')}
    </div>

    <div class="detail-section">
      <div class="detail-section-title">Notes (${notes.length})</div>
      ${notes.length === 0 ? '<p style="font-size:13px;color:var(--text-3)">No notes yet.</p>' :
        notes.slice(0,3).map(n => `<div style="padding:8px;background:var(--bg);border-radius:6px;margin-bottom:6px">
          <div style="font-size:13px;font-weight:500;margin-bottom:3px">${n.title}</div>
          <div style="font-size:12.5px;color:var(--text-2)">${n.body}</div>
        </div>`).join('')}
    </div>

    <div class="detail-section" style="border-bottom:none">
      <div class="detail-section-title">Actions</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        ${c.email ? `<a href="mailto:${c.email}" class="btn-secondary" style="font-size:13px;padding:7px 12px">📧 Send Email</a>` : ''}
        ${c.phone ? `<a href="tel:${c.phone}" class="btn-secondary" style="font-size:13px;padding:7px 12px">📞 Call</a>` : ''}
        <button class="btn-secondary" style="font-size:13px;padding:7px 12px" onclick="closeDetail();location.href='emails.html?contact=${id}'">Log Email</button>
        <button class="btn-danger" style="font-size:13px" onclick="deleteContact('${id}')">Delete</button>
      </div>
    </div>
  `;
  openDetail('contactDetail');
}

function field(label, value) {
  return `<div class="detail-field"><span class="detail-field-label">${label}</span><span class="detail-field-value">${value}</span></div>`;
}

async function exportContacts() {
  const contacts = await DB.getContacts();
  exportCSV(contacts.map(c => ({
    Name: c.name, Company: c.company, Email: c.email, Phone: c.phone,
    Title: c.title, Status: c.status, Tags: (c.tags||[]).join(';'), Added: formatDate(c.createdAt)
  })), 'contacts.csv');
}

async function importContacts(input) {
  const file = input.files[0];
  if (!file) return;
  importCSV(file, async (rows) => {
    let count = 0;
    for (const r of rows) {
      if (!r.Name && !r.name) continue;
      await DB.addContact({
        name: r.Name || r.name || '',
        company: r.Company || r.company || '',
        email: r.Email || r.email || '',
        phone: r.Phone || r.phone || '',
        title: r.Title || r.title || '',
        status: r.Status || r.status || 'Lead',
        tags: (r.Tags || r.tags || '').split(';').filter(Boolean),
      });
      count++;
    }
    toast(`Imported ${count} contacts`, 'success');
    renderContacts();
  });
  input.value = '';
}

// Auto-open add form if ?new=1
if (getParam('new') === '1') setTimeout(openAddContact, 100);

renderContacts();
