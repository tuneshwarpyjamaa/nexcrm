// =============================================
// NexCRM — App Utilities
// =============================================

// ---- Service Worker Registration (PWA) ----
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((reg) => {
        console.log('[NexCRM] Service Worker registered:', reg.scope);
        // Check for updates periodically
        setInterval(() => reg.update(), 60 * 60 * 1000); // hourly
      })
      .catch((err) => console.warn('[NexCRM] SW registration failed:', err));
  });
}

// ---- PWA Install Prompt ----
let deferredInstallPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredInstallPrompt = e;
  // Show install banner if not dismissed before
  if (!localStorage.getItem('nexcrm_pwa_dismissed')) {
    showInstallBanner();
  }
});

function showInstallBanner() {
  if (!deferredInstallPrompt) return;
  const banner = document.createElement('div');
  banner.className = 'pwa-install-banner';
  banner.innerHTML = `
    <div class="pwa-install-content">
      <span class="pwa-install-icon">📱</span>
      <div class="pwa-install-text">
        <strong>Install NexCRM</strong>
        <span>Add to home screen for a faster, offline-ready experience</span>
      </div>
    </div>
    <div class="pwa-install-actions">
      <button class="pwa-install-btn" onclick="installPWA()">Install</button>
      <button class="pwa-dismiss-btn" onclick="dismissInstall(this)">✕</button>
    </div>
  `;
  document.body.appendChild(banner);
  requestAnimationFrame(() => banner.classList.add('show'));
}

function installPWA() {
  if (!deferredInstallPrompt) return;
  deferredInstallPrompt.prompt();
  deferredInstallPrompt.userChoice.then((result) => {
    if (result.outcome === 'accepted') {
      toast('NexCRM installed! 🎉', 'success');
    }
    deferredInstallPrompt = null;
    const banner = document.querySelector('.pwa-install-banner');
    if (banner) banner.remove();
  });
}

function dismissInstall(btn) {
  localStorage.setItem('nexcrm_pwa_dismissed', '1');
  const banner = btn.closest('.pwa-install-banner');
  if (banner) { banner.classList.remove('show'); setTimeout(() => banner.remove(), 300); }
}

// ---- Offline Status Indicator ----
window.addEventListener('online', () => {
  document.body.classList.remove('is-offline');
  toast('Back online ✓', 'success');
});

window.addEventListener('offline', () => {
  document.body.classList.add('is-offline');
  toast('You are offline — changes saved locally', 'error');
});

if (!navigator.onLine) {
  document.body.classList.add('is-offline');
}

// Authentication check
window.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = 'login.html';
  }
});

function logout() {
  localStorage.removeItem('access_token');
  window.location.href = 'login.html';
}

// ---- Sidebar Toggle ----
function toggleSidebar() {
  const s = document.getElementById('sidebar');
  const m = document.querySelector('.main-content');
  const isMobile = window.innerWidth <= 768;

  if (isMobile) {
    // Mobile: overlay sidebar
    s.classList.toggle('mobile-open');
    let backdrop = document.querySelector('.sidebar-backdrop');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.className = 'sidebar-backdrop';
      backdrop.addEventListener('click', closeMobileSidebar);
      document.body.appendChild(backdrop);
    }
    if (s.classList.contains('mobile-open')) {
      requestAnimationFrame(() => backdrop.classList.add('show'));
    } else {
      backdrop.classList.remove('show');
    }
  } else {
    // Desktop: collapse sidebar
    s.classList.toggle('collapsed');
    if (m) m.classList.toggle('collapsed');
  }
}

function closeMobileSidebar() {
  const s = document.getElementById('sidebar');
  const backdrop = document.querySelector('.sidebar-backdrop');
  s.classList.remove('mobile-open');
  if (backdrop) backdrop.classList.remove('show');
}

// Close mobile sidebar when clicking a nav link
document.addEventListener('click', (e) => {
  if (window.innerWidth <= 768 && e.target.closest('.sidebar .nav-item')) {
    closeMobileSidebar();
  }
});

// ---- Mobile search box expand on tap ----
document.addEventListener('click', (e) => {
  if (window.innerWidth > 768) return;
  const searchBox = e.target.closest('.search-box');
  if (searchBox && !searchBox.classList.contains('expanded')) {
    e.preventDefault();
    searchBox.classList.add('expanded');
    const input = searchBox.querySelector('input');
    if (input) input.focus();
    return;
  }
  // Click outside search — collapse it
  if (!e.target.closest('.search-box') && !e.target.closest('.search-results')) {
    document.querySelectorAll('.search-box.expanded').forEach(sb => sb.classList.remove('expanded'));
  }
});

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
  if (!n) return '₹0';
  const num = parseFloat(n);
  if (num >= 10000000) return '₹' + (num/10000000).toFixed(1) + 'Cr';
  if (num >= 100000) return '₹' + (num/100000).toFixed(1) + 'L';
  if (num >= 1000) return '₹' + (num/1000).toFixed(1) + 'K';
  return '₹' + num.toLocaleString('en-IN');
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
  const bg = hexToRgba(color, 0.10);
  return `<span style="background:${bg};color:${color};padding:3px 9px;border-radius:20px;font-size:11.5px;font-weight:500">${stage}</span>`;
}

function hexToRgba(hex, alpha) {
  const h = (hex || '').replace('#', '');
  if (h.length !== 6) return `rgba(107,114,128,${alpha})`;
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return `rgba(${r},${g},${b},${alpha})`;
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
  searchTimer = setTimeout(async () => {
    const results = [];
    const contacts = await DB.getContacts();
    const deals = await DB.getDeals();
    const tasks = await DB.getTasks();
    contacts.filter(c => c.name.toLowerCase().includes(q.toLowerCase()) || (c.company||'').toLowerCase().includes(q.toLowerCase())).slice(0,4).forEach(c => {
      results.push({ type: 'Contact', name: c.name, sub: c.company, link: 'contacts.html', id: c.id, icon: 'contact' });
    });
    deals.filter(d => d.title.toLowerCase().includes(q.toLowerCase())).slice(0,3).forEach(d => {
      results.push({ type: 'Deal', name: d.title, sub: formatMoney(d.value), link: 'deals.html', id: d.id, icon: 'deal' });
    });
    tasks.filter(t => t.title.toLowerCase().includes(q.toLowerCase())).slice(0,3).forEach(t => {
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
