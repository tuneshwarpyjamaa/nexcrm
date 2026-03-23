// =============================================
// NexCRM — Dashboard
// =============================================

async function renderDashboard() {
  const [contacts, deals, tasks, notes] = await Promise.all([
    DB.getContacts(),
    DB.getDeals(),
    DB.getTasks(),
    DB.getNotes()
  ]);

  let totalPipeline = 0;
  let wonValue = 0;
  let activeDealsCount = 0;

  for (let i = 0; i < deals.length; i++) {
    const d = deals[i];
    if (d.stage === 'Won') {
      wonValue += parseFloat(d.value || 0);
    } else if (d.stage !== 'Lost') {
      totalPipeline += parseFloat(d.value || 0);
      activeDealsCount++;
    }
  }

  const overdueTasks = [];
  let openTasksCount = 0;
  const now = new Date();

  for (let i = 0; i < tasks.length; i++) {
    const t = tasks[i];
    if (!t.done) {
      openTasksCount++;
      if (t.dueDate && new Date(t.dueDate + 'T00:00:00') < now) {
        overdueTasks.push(t);
      }
    }
  }

  // Stats
  document.getElementById('statsGrid').innerHTML = [
    { label: 'Total Contacts', value: contacts.length, icon: '👥', link: 'contacts.html', color: '#2563eb' },
    { label: 'Active Deals', value: activeDealsCount, icon: '💼', link: 'deals.html', color: '#7c3aed' },
    { label: 'Pipeline Value', value: formatMoney(totalPipeline), icon: '📈', link: 'deals.html', color: '#16a34a' },
    { label: 'Won Revenue', value: formatMoney(wonValue), icon: '🏆', link: 'deals.html', color: '#d97706' },
    { label: 'Open Tasks', value: openTasksCount, icon: '✅', link: 'tasks.html', color: '#dc2626', delta: overdueTasks.length > 0 ? `${overdueTasks.length} overdue` : null, negative: true },
    { label: 'Notes', value: notes.length, icon: '📝', link: 'notes.html', color: '#0891b2' },
  ].map(s => `
    <div class="stat-card" onclick="location.href='${s.link}'" style="border-top: 3px solid ${s.color}">
      <div class="stat-label">${s.label}</div>
      <div class="stat-value" style="color:${s.color}">${s.value}</div>
      ${s.delta ? `<div class="stat-delta ${s.negative ? 'negative' : ''}">${s.delta}</div>` : '<div style="height:16px"></div>'}
    </div>
  `).join('');

  // Activity
  const activity = await DB.getActivity();
  document.getElementById('activityCount').textContent = Math.min(activity.length, 99);
  if (activity.length === 0) {
    document.getElementById('activityList').innerHTML = '<p class="empty-state">No activity yet.</p>';
  } else {
    document.getElementById('activityList').innerHTML = activity.slice(0, 8).map(a => `
      <div class="activity-item">
        <div class="activity-dot ${a.color || 'blue'}"></div>
        <div class="activity-text">${a.text}</div>
        <div class="activity-time">${relativeTime(a.time)}</div>
      </div>
    `).join('');
  }

  // Tasks
  const pending = tasks.filter(t => !t.done).sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate)).slice(0, 5);
  if (pending.length === 0) {
    document.getElementById('dashTaskList').innerHTML = '<p class="empty-state">No pending tasks. 🎉</p>';
  } else {
    document.getElementById('dashTaskList').innerHTML = pending.map(t => `
      <div class="task-item">
        <div class="task-check ${t.done ? 'done' : ''}" onclick="toggleTask('${t.id}', event)"></div>
        <div class="task-title ${t.done ? 'done' : ''}">${t.title}</div>
        ${dueBadge(t.dueDate)}
      </div>
    `).join('');
  }

  // Pipeline chart
  const STAGES = ['Lead','Meeting','Proposal','Negotiation','Won'];
  const stageCounts = {};
  const stageValues = {};
  STAGES.forEach(s => { stageCounts[s] = 0; stageValues[s] = 0; });
  deals.forEach(d => { if (stageCounts[d.stage] !== undefined) { stageCounts[d.stage]++; stageValues[d.stage] += parseFloat(d.value || 0); } });
  const maxVal = Math.max(...Object.values(stageValues), 1);
  const BAR_COLORS = { 'Lead': '#6b7280', 'Meeting': '#0891b2', 'Proposal': '#7c3aed', 'Negotiation': '#d97706', 'Won': '#16a34a' };
  document.getElementById('pipelineChart').innerHTML = STAGES.map(stage => `
    <div class="pipeline-stage">
      <div class="pipeline-label">${stage}</div>
      <div class="pipeline-bar-wrap">
        <div class="pipeline-bar" style="width:${Math.max((stageValues[stage]/maxVal)*100, stageValues[stage]>0?8:0)}%;background:${BAR_COLORS[stage]}">
          ${stageValues[stage] > 0 ? `<span>${formatMoney(stageValues[stage])}</span>` : ''}
        </div>
      </div>
      <div class="pipeline-count">${stageCounts[stage]}</div>
    </div>
  `).join('');

  // Top contacts
  const topC = contacts.filter(c => c.status === 'Customer' || (c.tags||[]).includes('vip') || (c.tags||[]).includes('hot')).slice(0,5);
  document.getElementById('topContacts').innerHTML = topC.length === 0
    ? '<p class="empty-state">No contacts yet.</p>'
    : topC.map(c => `
      <div class="contact-row" onclick="location.href='contacts.html'">
        ${avatarHTML(c.name)}
        <div class="contact-info">
          <div class="contact-name">${c.name}</div>
          <div class="contact-company">${c.company || ''}</div>
        </div>
        ${statusTag(c.status)}
      </div>
    `).join('');

  // Hot deals
  const hotD = deals.filter(d => d.stage !== 'Won' && d.stage !== 'Lost').sort((a, b) => parseFloat(b.value) - parseFloat(a.value)).slice(0, 5);
  document.getElementById('hotDeals').innerHTML = hotD.length === 0
    ? '<p class="empty-state">No active deals.</p>'
    : hotD.map(d => `
      <div class="contact-row" onclick="location.href='deals.html'">
        <div style="width:8px;height:8px;border-radius:50%;background:${STAGE_COLORS[d.stage]||'#999'};flex-shrink:0;margin-top:2px"></div>
        <div class="contact-info">
          <div class="contact-name">${d.title}</div>
          <div class="contact-company">${d.company || ''}</div>
        </div>
        <span style="font-size:13px;font-weight:600;color:var(--green);font-family:var(--mono)">${formatMoney(d.value)}</span>
      </div>
    `).join('');
}

async function toggleTask(id, e) {
  e.stopPropagation();
  const t = await DB.getTask(id);
  if (!t) return;
  await DB.updateTask(id, { done: !t.done });
  if (!t.done) toast('Task completed! ✓', 'success');
  renderDashboard();
}

renderDashboard();
