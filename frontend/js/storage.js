// =============================================
// NexCRM — Storage Layer
// API-based storage using backend
// =============================================

function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
}

let _cache = { contacts: null, deals: null, tasks: null, notes: null };

const DB = {
  // --- Contacts ---
  getContacts: async () => {
    if (_cache.contacts) return _cache.contacts;
    const response = await fetch('/api/contacts', {
      headers: getAuthHeaders()
    });
    _cache.contacts = await response.json();
    return _cache.contacts;
  },
  addContact: async (c) => {
    _cache.contacts = null;
    c.id = 'c_' + Date.now();
    c.createdAt = new Date().toISOString();
    c.tags = c.tags || [];
    const response = await fetch('/api/contacts', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(c)
    });
    const newContact = await response.json();
    await DB.addActivity('contact', `Added contact <strong>${c.name}</strong>`);
    return newContact;
  },
  updateContact: async (id, data) => {
    _cache.contacts = null;
    const response = await fetch(`/api/contacts/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return await response.json();
  },
  deleteContact: async (id) => {
    _cache.contacts = null;
    const contact = await DB.getContact(id);
    await fetch(`/api/contacts/${id}`, { 
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (contact) await DB.addActivity('contact', `Deleted contact <strong>${contact.name}</strong>`);
  },
  getContact: async (id) => {
    const contacts = await DB.getContacts();
    return contacts.find(c => c.id === id);
  },

  // --- Deals ---
  getDeals: async () => {
    if (_cache.deals) return _cache.deals;
    const response = await fetch('/api/deals', {
      headers: getAuthHeaders()
    });
    _cache.deals = await response.json();
    return _cache.deals;
  },
  addDeal: async (d) => {
    _cache.deals = null;
    d.id = 'd_' + Date.now();
    d.createdAt = new Date().toISOString();
    d.stage = d.stage || 'Lead';
    const response = await fetch('/api/deals', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(d)
    });
    const newDeal = await response.json();
    await DB.addActivity('deal', `New deal: <strong>${d.title}</strong>`, 'green');
    return newDeal;
  },
  updateDeal: async (id, data) => {
    _cache.deals = null;
    const response = await fetch(`/api/deals/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return await response.json();
  },
  deleteDeal: async (id) => {
    _cache.deals = null;
    const deal = await DB.getDeal(id);
    await fetch(`/api/deals/${id}`, { 
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (deal) await DB.addActivity('deal', `Closed deal: <strong>${deal.title}</strong>`, 'red');
  },
  getDeal: async (id) => {
    const deals = await DB.getDeals();
    return deals.find(d => d.id === id);
  },

  // --- Tasks ---
  getTasks: async () => {
    if (_cache.tasks) return _cache.tasks;
    const response = await fetch('/api/tasks', {
      headers: getAuthHeaders()
    });
    _cache.tasks = await response.json();
    return _cache.tasks;
  },
  addTask: async (t) => {
    _cache.tasks = null;
    t.id = 't_' + Date.now();
    t.createdAt = new Date().toISOString();
    t.done = false;
    const response = await fetch('/api/tasks', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(t)
    });
    const newTask = await response.json();
    await DB.addActivity('task', `Task added: <strong>${t.title}</strong>`, 'yellow');
    return newTask;
  },
  updateTask: async (id, data) => {
    _cache.tasks = null;
    const response = await fetch(`/api/tasks/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return await response.json();
  },
  deleteTask: async (id) => {
    _cache.tasks = null;
    await fetch(`/api/tasks/${id}`, { 
      method: 'DELETE',
      headers: getAuthHeaders()
    });
  },
  getTask: async (id) => {
    const tasks = await DB.getTasks();
    return tasks.find(t => t.id === id);
  },

  // --- Notes ---
  getNotes: async () => {
    if (_cache.notes) return _cache.notes;
    const response = await fetch('/api/notes', {
      headers: getAuthHeaders()
    });
    _cache.notes = await response.json();
    return _cache.notes;
  },
  addNote: async (n) => {
    _cache.notes = null;
    n.id = 'n_' + Date.now();
    n.createdAt = new Date().toISOString();
    const response = await fetch('/api/notes', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(n)
    });
    const newNote = await response.json();
    await DB.addActivity('note', `Note: <strong>${n.title}</strong>`);
    return newNote;
  },
  updateNote: async (id, data) => {
    _cache.notes = null;
    const response = await fetch(`/api/notes/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return await response.json();
  },
  deleteNote: async (id) => {
    _cache.notes = null;
    await fetch(`/api/notes/${id}`, { 
      method: 'DELETE',
      headers: getAuthHeaders()
    });
  },

  // --- Emails (logged) ---
  getEmails: async () => {
    const response = await fetch('/api/emails', {
      headers: getAuthHeaders()
    });
    return await response.json();
  },
  addEmail: async (e) => {
    e.id = 'e_' + Date.now();
    e.sentAt = new Date().toISOString();
    const response = await fetch('/api/emails', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(e)
    });
    const newEmail = await response.json();
    await DB.addActivity('email', `Email sent to <strong>${e.to}</strong>`, 'blue');
    return newEmail;
  },
  deleteEmail: async (id) => {
    await fetch(`/api/emails/${id}`, { 
      method: 'DELETE',
      headers: getAuthHeaders()
    });
  },
  updateEmail: async (id, data) => {
    const response = await fetch(`/api/emails/${id}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return await response.json();
  },
  getEmailStats: async () => {
    const response = await fetch('/api/emails/stats', {
      headers: getAuthHeaders()
    });
    return await response.json();
  },

  // --- Activity Log ---
  getActivity: async () => {
    const response = await fetch('/api/activity', {
      headers: getAuthHeaders()
    });
    return await response.json();
  },
  addActivity: async (type, text, color = 'blue') => {
    await fetch('/api/activity', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ type, text, color })
    });
  },

  // --- Settings ---
  getSettings: async () => {
    const response = await fetch('/api/settings', {
      headers: getAuthHeaders()
    });
    return await response.json();
  },
  saveSettings: async (s) => {
    await fetch('/api/settings', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(s)
    });
  },

  // --- Subscriptions ---
  getSubscription: async () => {
    const response = await fetch('/api/subscriptions/me', {
      headers: getAuthHeaders()
    });
    if (!response.ok) return null;
    return await response.json();
  },
  upgradeSubscription: async () => {
    const response = await fetch('/api/subscriptions/subscribe', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ action: 'upgrade', plan_name: 'premium' })
    });
    return await response.json();
  },
};


