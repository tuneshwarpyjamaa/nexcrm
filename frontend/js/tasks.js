// =============================================
// NexCRM — Tasks
// =============================================

let editingTaskId = null;

async function renderTasks() {
  const all = await DB.getTasks();
  const contacts = await DB.getContacts();
  const q = document.getElementById('taskFilter').value.toLowerCase();
  const sf = document.getElementById('taskStatusFilter').value;
  const pf = document.getElementById('taskPriorityFilter').value;

  let tasks = all;
  if (q) tasks = tasks.filter(t => t.title.toLowerCase().includes(q));
  if (sf === 'open') tasks = tasks.filter(t => !t.done);
  if (sf === 'done') tasks = tasks.filter(t => t.done);
  if (pf) tasks = tasks.filter(t => t.priority === pf);

  // Sort: overdue first, then by due date, then by priority
  const pOrder = { High: 0, Medium: 1, Low: 2 };
  tasks.sort((a, b) => {
    if (a.done !== b.done) return a.done ? 1 : -1;
    if (a.dueDate && b.dueDate) return new Date(a.dueDate) - new Date(b.dueDate);
    if (a.dueDate) return -1;
    if (b.dueDate) return 1;
    return (pOrder[a.priority] || 1) - (pOrder[b.priority] || 1);
  });

  // Stats
  const overdue = all.filter(t => !t.done && t.dueDate && new Date(t.dueDate+'T00:00:00') < new Date()).length;
  document.getElementById('taskStats').innerHTML = [
    { label: 'Open', value: all.filter(t=>!t.done).length, color: 'var(--accent)' },
    { label: 'Overdue', value: overdue, color: 'var(--red)' },
    { label: 'Due Today', value: all.filter(t=>!t.done && t.dueDate && new Date(t.dueDate+'T00:00:00').toDateString() === new Date().toDateString()).length, color: 'var(--yellow)' },
    { label: 'Completed', value: all.filter(t=>t.done).length, color: 'var(--green)' },
  ].map(m => `<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:10px 16px;box-shadow:var(--shadow)">
    <div style="font-size:11.5px;color:var(--text-3);font-weight:500;margin-bottom:2px">${m.label}</div>
    <div style="font-size:22px;font-weight:600;color:${m.color};font-family:var(--mono)">${m.value}</div>
  </div>`).join('');

  if (tasks.length === 0) {
    document.getElementById('tasksTable').innerHTML = `<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--text-3)">No tasks found. <a href="#" onclick="openAddTask()" style="color:var(--accent)">Add a task →</a></td></tr>`;
    return;
  }

  document.getElementById('tasksTable').innerHTML = tasks.map(t => {
    const c = t.contactId ? contacts.find(c => c.id === t.contactId) : null;
    return `
      <tr style="${t.done ? 'opacity:0.55' : ''}">
        <td>
          <div class="task-check ${t.done ? 'done' : ''}" onclick="toggleTask('${t.id}')"></div>
        </td>
        <td>
          <div style="font-weight:500;${t.done?'text-decoration:line-through;color:var(--text-3)':''}">${t.title}</div>
          ${t.notes ? `<div style="font-size:12px;color:var(--text-3);margin-top:2px">${t.notes.substring(0,60)}${t.notes.length>60?'...':''}</div>` : ''}
        </td>
        <td>${c ? `<div style="display:flex;align-items:center;gap:6px">${avatarHTML(c.name,22)}<span style="font-size:13px">${c.name}</span></div>` : '—'}</td>
        <td>${priorityTag(t.priority)}</td>
        <td>${dueBadge(t.dueDate)}</td>
        <td style="font-size:12.5px;color:var(--text-3)">${formatDate(t.createdAt)}</td>
        <td>
          <div style="display:flex;gap:4px">
            <button class="btn-icon" onclick="openEditTask('${t.id}')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>
            <button class="btn-icon" onclick="deleteTask('${t.id}')" style="color:var(--red)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3,6 5,6 21,6"/><path d="M19,6l-1,14a2 2 0 0 1-2,2H8a2 2 0 0 1-2-2L5,6"/></svg></button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

async function toggleTask(id) {
  const t = await DB.getTask(id);
  if (!t) return;
  await DB.updateTask(id, { done: !t.done });
  if (!t.done) toast('Task completed! ✓', 'success');
  renderTasks();
}

async function openAddTask() {
  editingTaskId = null;
  document.getElementById('taskModalTitle').textContent = 'Add Task';
  document.getElementById('t_title').value = '';
  document.getElementById('t_due').value = '';
  document.getElementById('t_priority').value = 'Medium';
  document.getElementById('t_notes').value = '';
  const contacts = await DB.getContacts();
  document.getElementById('t_contact').innerHTML = '<option value="">No contact linked</option>' +
    contacts.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  openModal('taskModal');
  setTimeout(() => document.getElementById('t_title').focus(), 100);
}

async function openEditTask(id) {
  const t = await DB.getTask(id);
  if (!t) return;
  editingTaskId = id;
  document.getElementById('taskModalTitle').textContent = 'Edit Task';
  document.getElementById('t_title').value = t.title || '';
  document.getElementById('t_due').value = t.dueDate || '';
  document.getElementById('t_priority').value = t.priority || 'Medium';
  document.getElementById('t_notes').value = t.notes || '';
  const contacts = await DB.getContacts();
  document.getElementById('t_contact').innerHTML = '<option value="">No contact linked</option>' +
    contacts.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  document.getElementById('t_contact').value = t.contactId || '';
  openModal('taskModal');
}

async function saveTask() {
  const title = document.getElementById('t_title').value.trim();
  if (!title) { toast('Task title is required', 'error'); return; }
  const data = {
    title,
    dueDate: document.getElementById('t_due').value,
    priority: document.getElementById('t_priority').value,
    contactId: document.getElementById('t_contact').value || null,
    notes: document.getElementById('t_notes').value.trim(),
  };
  if (editingTaskId) {
    await DB.updateTask(editingTaskId, data);
    toast('Task updated', 'success');
  } else {
    await DB.addTask(data);
    toast('Task added', 'success');
  }
  closeModal();
  renderTasks();
}

async function deleteTask(id) {
  if (!confirm('Delete this task?')) return;
  await DB.deleteTask(id);
  toast('Task deleted');
  renderTasks();
}

async function clearDone() {
  const allTasks = await DB.getTasks();
  const done = allTasks.filter(t => t.done);
  if (done.length === 0) { toast('No completed tasks to clear'); return; }
  if (!confirm(`Clear ${done.length} completed tasks?`)) return;
  for (const t of done) {
    await DB.deleteTask(t.id);
  }
  toast(`Cleared ${done.length} tasks`);
  renderTasks();
}

if (getParam('new') === '1') setTimeout(openAddTask, 100);
renderTasks();
