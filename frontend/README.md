# NexCRM — Lightweight CRM for Small Businesses

A complete, offline-first CRM that runs in any browser. No server required.

## 🚀 Quick Start

1. Extract the ZIP file
2. Open `index.html` in any modern browser
3. That's it — demo data is pre-loaded!

## 📋 Features

### Core CRM (Everything the big ones do)
- **Contacts** — Full contact profiles with company, title, email, phone, LinkedIn, tags, source tracking
- **Deals Pipeline** — Kanban board + list view with stages: Lead → Meeting → Proposal → Negotiation → Won/Lost
- **Tasks** — Task management with priorities, due dates, contact linking, overdue alerts
- **Email Log** — Track email communications, open in mail client, log by contact
- **Notes** — Freeform notes linked to contacts
- **Reports** — Pipeline analytics, win rate, weighted forecast, contact breakdown, lead sources
- **Activity Feed** — Auto-logged activity timeline

### Features Big CRMs Charge Extra For
- 🔍 **Global Search** — Search contacts, deals, tasks instantly
- 📊 **Weighted Pipeline** — Forecast revenue based on probability
- 📥 **CSV Import/Export** — Import contacts from spreadsheets, export any data
- 💾 **Full Backup/Restore** — Export entire database as JSON, restore anytime
- 🎯 **Quick Add** — Add anything from any page in 2 clicks
- 📱 **Responsive** — Works on mobile and tablet
- 🔒 **Offline & Private** — All data stays on your device (localStorage)

### What Makes NexCRM Different
- **Zero setup** — Just open the HTML file
- **No subscription** — Own your data forever
- **No internet required** — Works completely offline
- **No bloat** — Fast, simple, focused

## 🗂️ File Structure

```
nexcrm/
├── index.html          Dashboard
├── contacts.html       Contact management
├── deals.html          Sales pipeline (Kanban + List)
├── tasks.html          Task tracking
├── emails.html         Email log
├── notes.html          Notes & call logs
├── reports.html        Analytics & reports
├── settings.html       Settings, backup & restore
├── css/
│   └── main.css        All styles
└── js/
    ├── storage.js      Data layer (localStorage)
    ├── app.js          Shared utilities
    ├── dashboard.js    Dashboard logic
    ├── contacts.js     Contacts logic
    ├── deals.js        Deals logic
    └── tasks.js        Tasks logic
```

## 💾 Data Storage

All data is stored in your browser's localStorage. Data persists between sessions on the same browser/device.

**To move data between devices:** Settings → Export All Data → import on new device.

## 🛠️ Tech Stack

- **HTML5** — Semantic markup
- **CSS3** — Custom properties, Grid, Flexbox (no frameworks)
- **Vanilla JavaScript** — No dependencies, no build tools
- **localStorage** — Browser storage for data persistence
- **Google Fonts** — DM Sans + DM Mono (loaded from CDN; works offline if cached)

## 📖 Tips

- Click any row to open a detail panel
- Use the pipeline board to drag deals between stages (click stage buttons in detail panel)
- Import contacts from Excel by saving as CSV first
- Set up regular JSON backups via Settings
- Use tags on contacts for segmentation (hot, vip, cold, etc.)

---