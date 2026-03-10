// =============================================
// NexCRM — App Utilities
// =============================================

// Authentication check
window.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/';
  }
});

// ---- Sidebar Toggle ----
function toggleSidebar() {
  const s = document.getElementById('sidebar');
  const m = document.querySelector('.main-content');
  s.classList.toggle('collapsed');
  if (m) m.classList.toggle('collapsed');
}

// ---- Toast Notifications ----
function toast(msg, type = 'default') {
  let wrap = document.querySelector('.toast-wrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.className = 'toast-wrap';
    document.body.appendChild(wrap);
  }
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  wrap.appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

// ---- Modal Helpers ----
function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('open');
}

function closeModal(e) {
  if (e && e.target !== e.currentTarget) return;
  document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
}

function closeQuickAdd() {
  document.getElementById('quickAddModal').classList.remove('open');
}

function showQuickAdd() {
  document.getElementById('quickAddModal').classList.add('open');
}

// ---- Detail Panel ----
function openDetail(panelId) {
  const overlay = document.getElementById('detailOverlay');
  const panel = document.getElementById(panelId);
  if (overlay) overlay.classList.add('open');
  if (panel) panel.classList.add('open');
}

function closeDetail() {
  document.querySelectorAll('.detail-overlay, .detail-panel').forEach(el => el.classList.remove('open'));
}

// ---- Avatar Color ----
const AVATAR_COLORS = ['#2563eb','#16a34a','#d97706','#dc2626','#7c3aed','#0891b2','#be185d','#854d0e'];
function avatarColor(name) {
  let h = 0;
  for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h);
  return AVATAR_COLORS[Math.abs(h) % AVATAR_COLORS.length];
}

function initials(name) {
  return (name || '?').split(' ').slice(0,2).map(w => w[0]).join('').toUpperCase();
}

function avatarHTML(name, size = 32) {
  return `<div class="avatar" style="background:${avatarColor(name)};width:${size}px;height:${size}px;font-size:${Math.floor(size*0.38)}px">${initials(name)}</div>`;
}

// ---- Date Helpers ----
function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function relativeTime(iso) {
  if (!iso) return '';
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days}d ago`;
  return formatDate(iso);
}

function dueBadge(dateStr) {
  if (!dateStr) return '';
  const today = new Date(); today.setHours(0,0,0,0);
  const due = new Date(dateStr + 'T00:00:00');
  const diff = Math.floor((due - today) / 86400000);
  if (diff < 0) return `<span class="task-due overdue">Overdue</span>`;
  if (diff === 0) return `<span class="task-due overdue">Today</span>`;
  if (diff <= 3) return `<span class="task-due">${formatDate(dateStr)}</span>`;
  return `<span class="task-due ok">${formatDate(dateStr)}</span>`;
}

// ---- Currency ----
function formatMoney(n) {
  if (!n) return '$0';
  const num = parseFloat(n);
  if (num >= 1000000) return '$' + (num/1000000).toFixed(1) + 'M';
  if (num >= 1000) return '$' + (num/1000).toFixed(1) + 'K';
  return '$' + num.toLocaleString();
}

// ---- Stage Colors ----
const STAGE_COLORS = {
  'Lead': '#6b7280',
  'Meeting': '#0891b2',
  'Proposal': '#7c3aed',
  'Negotiation': '#d97706',
  'Won': '#16a34a',
  'Lost': '#dc2626',
};

function stageTag(stage) {
  const color = STAGE_COLORS[stage] || '#6b7280';
  return `<span style="background:${color}18;color:${color};padding:3px 9px;border-radius:20px;font-size:11.5px;font-weight:500">${stage}</span>`;
}

// ---- Status Tags ----
const STATUS_MAP = { 'Customer': 'tag-green', 'Lead': 'tag-blue', 'Prospect': 'tag-yellow', 'Inactive': 'tag-gray', 'Partner': 'tag-purple' };
function statusTag(status) {
  return `<span class="tag ${STATUS_MAP[status] || 'tag-gray'}">${status || 'Lead'}</span>`;
}

// ---- Priority Tags ----
const PRIORITY_MAP = { 'High': 'tag-red', 'Medium': 'tag-yellow', 'Low': 'tag-gray' };
function priorityTag(p) {
  return `<span class="tag ${PRIORITY_MAP[p] || 'tag-gray'}">${p || 'Medium'}</span>`;
}

// ---- Global Search ----
let searchTimer;
function globalSearch(q) {
  clearTimeout(searchTimer);
  const box = document.getElementById('searchResults');
  if (!q || q.length < 2) { box.classList.remove('open'); return; }
  searchTimer = setTimeout(() => {
    const results = [];
    DB.getContacts().filter(c => c.name.toLowerCase().includes(q.toLowerCase()) || (c.company||'').toLowerCase().includes(q.toLowerCase())).slice(0,4).forEach(c => {
      results.push({ type: 'Contact', name: c.name, sub: c.company, link: 'contacts.html', id: c.id, icon: 'contact' });
    });
    DB.getDeals().filter(d => d.title.toLowerCase().includes(q.toLowerCase())).slice(0,3).forEach(d => {
      results.push({ type: 'Deal', name: d.title, sub: formatMoney(d.value), link: 'deals.html', id: d.id, icon: 'deal' });
    });
    DB.getTasks().filter(t => t.title.toLowerCase().includes(q.toLowerCase())).slice(0,3).forEach(t => {
      results.push({ type: 'Task', name: t.title, sub: t.dueDate || '', link: 'tasks.html', id: t.id, icon: 'task' });
    });

    const icons = {
      contact: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
      deal: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>`,
      task: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>`,
    };

    if (results.length === 0) {
      box.innerHTML = `<div class="search-result-item"><div class="search-result-name" style="color:var(--text-3)">No results found</div></div>`;
    } else {
      box.innerHTML = results.map(r => `
        <div class="search-result-item" onclick="location.href='${r.link}'">
          <div class="search-result-icon">${icons[r.icon]}</div>
          <div>
            <div class="search-result-name">${r.name}</div>
            <div class="search-result-type">${r.type} ${r.sub ? '· ' + r.sub : ''}</div>
          </div>
        </div>
      `).join('');
    }
    box.classList.add('open');
  }, 200);
}

// Close search on outside click
document.addEventListener('click', (e) => {
  if (!e.target.closest('.search-box') && !e.target.closest('.search-results')) {
    document.getElementById('searchResults')?.classList.remove('open');
  }
});

// Close modal on ESC
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
    closeDetail();
  }
});

// ---- URL params helper ----
function getParam(key) {
  return new URLSearchParams(window.location.search).get(key);
}

// ---- Export to CSV ----
function exportCSV(data, filename) {
  if (!data.length) { toast('Nothing to export', 'error'); return; }
  const keys = Object.keys(data[0]);
  const csv = [keys.join(','), ...data.map(row => keys.map(k => JSON.stringify(row[k] ?? '')).join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = filename; a.click();
  toast(`Exported ${data.length} records`);
}

// ---- Import from CSV ----
function importCSV(file, callback) {
  const reader = new FileReader();
  reader.onload = (e) => {
    const lines = e.target.result.split('\n').filter(Boolean);
    const headers = lines[0].split(',');
    const data = lines.slice(1).map(line => {
      const vals = line.split(',');
      const obj = {};
      headers.forEach((h, i) => obj[h.trim()] = (vals[i] || '').replace(/^"|"$/g, '').trim());
      return obj;
    });
    callback(data);
  };
  reader.readAsText(file);
}
