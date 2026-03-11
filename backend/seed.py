"""
Seed script: clears all data and inserts 10 realistic records per table.
Run with:  python seed.py
"""

import asyncio
import asyncpg
import os
import json
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()


async def main():
    conn = await asyncpg.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
    )

    # ── Wipe all existing data ──────────────────────────────────────────
    print("Clearing all tables...")
    await conn.execute("DELETE FROM activity")
    await conn.execute("DELETE FROM emails")
    await conn.execute("DELETE FROM notes")
    await conn.execute("DELETE FROM tasks")
    await conn.execute("DELETE FROM deals")
    await conn.execute("DELETE FROM contacts")
    await conn.execute("DELETE FROM settings")
    print("All tables cleared.\n")

    now = datetime.now()

    # ── Contacts ────────────────────────────────────────────────────────
    contacts = [
        ("c_001", "Priya Sharma", "priya.sharma@infosys.com", "+91 98765 43210", "Infosys", "VP of Engineering", "Active", json.dumps(["Enterprise", "Tech"]), "https://linkedin.com/in/priyasharma", "Key decision maker for cloud migration project."),
        ("c_002", "Rahul Mehta", "rahul.mehta@tcs.com", "+91 87654 32109", "TCS", "Head of Procurement", "Active", json.dumps(["Enterprise", "IT Services"]), "https://linkedin.com/in/rahulmehta", "Interested in annual licensing deal."),
        ("c_003", "Ananya Reddy", "ananya.r@wipro.com", "+91 76543 21098", "Wipro", "CTO", "Lead", json.dumps(["Tech", "C-Suite"]), "https://linkedin.com/in/ananyareddy", "Met at TechSummit 2026. Exploring AI integration."),
        ("c_004", "Vikram Desai", "vikram.desai@zoho.com", "+91 65432 10987", "Zoho", "Product Manager", "Active", json.dumps(["SaaS", "Product"]), "https://linkedin.com/in/vikramdesai", "Evaluating CRM migration from legacy system."),
        ("c_005", "Meera Nair", "meera.nair@freshworks.com", "+91 54321 09876", "Freshworks", "Director of Sales", "Prospect", json.dumps(["SaaS", "Sales"]), "https://linkedin.com/in/meeranair", "Looking for custom integrations."),
        ("c_006", "Arjun Patel", "arjun.patel@reliance.com", "+91 43210 98765", "Reliance Digital", "IT Manager", "Active", json.dumps(["Retail", "Enterprise"]), "https://linkedin.com/in/arjunpatel", "Managing retail POS system rollout."),
        ("c_007", "Kavitha Iyer", "kavitha.i@hcltech.com", "+91 32109 87654", "HCL Technologies", "Chief Data Officer", "Lead", json.dumps(["Data", "C-Suite"]), "https://linkedin.com/in/kavithaiyer", "Data analytics platform evaluation in progress."),
        ("c_008", "Sanjay Gupta", "sanjay.gupta@razorpay.com", "+91 21098 76543", "Razorpay", "Engineering Lead", "Active", json.dumps(["Fintech", "Startup"]), "https://linkedin.com/in/sanjaygupta", "Building payment reconciliation dashboard."),
        ("c_009", "Deepika Joshi", "deepika.j@swiggy.com", "+91 10987 65432", "Swiggy", "Operations Head", "Prospect", json.dumps(["Foodtech", "Operations"]), "https://linkedin.com/in/deepikajoshi", "Exploring logistics optimization tools."),
        ("c_010", "Rohan Kapoor", "rohan.kapoor@byju.com", "+91 99887 76655", "BYJU'S", "VP of Technology", "Lead", json.dumps(["EdTech", "Tech"]), "https://linkedin.com/in/rohankapoor", "Interested in learning management integration."),
    ]
    for c in contacts:
        created = now - timedelta(days=30 - contacts.index(c) * 3)
        await conn.execute(
            'INSERT INTO contacts (id, name, email, phone, company, title, status, tags, linkedin, notes, "createdAt") VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)',
            *c, created,
        )
    print("[OK] 10 contacts inserted")

    # ── Deals ───────────────────────────────────────────────────────────
    deals = [
        ("d_001", "Infosys Cloud Migration", "c_001", "Infosys", 450000.0, "Proposal", 70, date(2026, 5, 15), "Multi-year cloud infrastructure deal."),
        ("d_002", "TCS Enterprise License", "c_002", "TCS", 320000.0, "Negotiation", 85, date(2026, 4, 30), "Annual enterprise license renewal."),
        ("d_003", "Wipro AI Integration", "c_003", "Wipro", 275000.0, "Meeting", 30, date(2026, 7, 1), "AI/ML platform integration pilot."),
        ("d_004", "Zoho CRM Migration", "c_004", "Zoho", 85000.0, "Meeting", 50, date(2026, 4, 15), "Legacy CRM to modern stack migration."),
        ("d_005", "Freshworks Custom API", "c_005", "Freshworks", 120000.0, "Proposal", 60, date(2026, 6, 1), "Custom API integration package."),
        ("d_006", "Reliance POS Rollout", "c_006", "Reliance Digital", 530000.0, "Won", 90, date(2026, 3, 31), "Nationwide POS system deployment."),
        ("d_007", "HCL Analytics Platform", "c_007", "HCL Technologies", 380000.0, "Lost", 0, date(2026, 8, 1), "Enterprise data analytics solution — lost to competitor."),
        ("d_008", "Razorpay Dashboard", "c_008", "Razorpay", 95000.0, "Won", 100, date(2026, 3, 1), "Payment reconciliation dashboard — signed."),
        ("d_009", "Swiggy Logistics Tool", "c_009", "Swiggy", 210000.0, "Lead", 20, date(2026, 9, 15), "Route optimization and logistics tool."),
        ("d_010", "BYJU'S LMS Integration", "c_010", "BYJU'S", 175000.0, "Proposal", 55, date(2026, 6, 30), "Learning management system integration."),
    ]
    for d in deals:
        created = now - timedelta(days=25 - deals.index(d) * 2)
        await conn.execute(
            'INSERT INTO deals (id, title, "contactId", company, value, stage, probability, "closeDate", notes, "createdAt") VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)',
            *d, created,
        )
    print("[OK] 10 deals inserted")

    # ── Tasks ───────────────────────────────────────────────────────────
    tasks = [
        ("t_001", "Follow up with Priya on cloud proposal", "c_001", date(2026, 3, 12), "High", False),
        ("t_002", "Send revised pricing to Rahul", "c_002", date(2026, 3, 11), "High", False),
        ("t_003", "Schedule demo for Ananya", "c_003", date(2026, 3, 15), "Normal", False),
        ("t_004", "Prepare migration roadmap for Zoho", "c_004", date(2026, 3, 18), "Normal", False),
        ("t_005", "Draft API spec for Freshworks", "c_005", date(2026, 3, 20), "Low", False),
        ("t_006", "Finalize Reliance POS contract", "c_006", date(2026, 3, 13), "High", False),
        ("t_007", "Send case study to Kavitha", "c_007", date(2026, 3, 14), "Normal", False),
        ("t_008", "Onboarding call with Razorpay team", "c_008", date(2026, 3, 10), "High", True),
        ("t_009", "Research Swiggy's logistics flow", "c_009", date(2026, 3, 22), "Low", False),
        ("t_010", "Prepare LMS integration timeline", "c_010", date(2026, 3, 25), "Normal", False),
    ]
    for t in tasks:
        created = now - timedelta(days=10 - tasks.index(t))
        await conn.execute(
            'INSERT INTO tasks (id, title, "contactId", "dueDate", priority, done, "createdAt") VALUES ($1,$2,$3,$4,$5,$6,$7)',
            *t, created,
        )
    print("[OK] 10 tasks inserted")

    # ── Notes ───────────────────────────────────────────────────────────
    notes = [
        ("n_001", "Infosys Meeting Notes", "Had a productive call with Priya. They want to migrate 200+ services to our cloud platform. Budget approved internally. Need proposal by next week.", "c_001", "Priya Sharma"),
        ("n_002", "TCS License Discussion", "Rahul confirmed they want to renew for 3 years. Needs 15% volume discount to get board approval. Competitor is offering similar terms.", "c_002", "Rahul Mehta"),
        ("n_003", "TechSummit 2026 Follow-up", "Met Ananya at TechSummit. She's exploring AI integration for testing automation. Wants a pilot with 50 engineers first.", "c_003", "Ananya Reddy"),
        ("n_004", "Zoho Migration Assessment", "Vikram shared current pain points: slow search, no API access, poor reporting. Perfect fit for our platform.", "c_004", "Vikram Desai"),
        ("n_005", "Freshworks API Requirements", "Meera needs bidirectional sync with Salesforce, HubSpot, and their internal ticketing system. Complex but doable.", "c_005", "Meera Nair"),
        ("n_006", "Reliance POS Demo Feedback", "Arjun loved the demo. Main concern is offline mode for tier-2/3 city stores. Need to highlight our offline-first architecture.", "c_006", "Arjun Patel"),
        ("n_007", "HCL Data Platform RFP", "Kavitha sent the formal RFP. Key requirements: real-time dashboards, data lake integration, SOC2 compliance. Response due April 5.", "c_007", "Kavitha Iyer"),
        ("n_008", "Razorpay Kickoff Complete", "Onboarding done. Sanjay's team is ramping up. First milestone: payment reconciliation dashboard live by March 25.", "c_008", "Sanjay Gupta"),
        ("n_009", "Swiggy Discovery Call", "Deepika outlined delivery logistics challenges. 500K+ daily orders, need sub-second route optimization. Interesting use case.", "c_009", "Deepika Joshi"),
        ("n_010", "BYJU'S Tech Stack Review", "Rohan shared their current stack. Running on AWS, using custom LMS. Want to integrate our analytics module into their platform.", "c_010", "Rohan Kapoor"),
    ]
    for n in notes:
        created = now - timedelta(days=15 - notes.index(n))
        await conn.execute(
            'INSERT INTO notes (id, title, body, "contactId", "contactName", "createdAt") VALUES ($1,$2,$3,$4,$5,$6)',
            *n, created,
        )
    print("[OK] 10 notes inserted")

    # ── Emails ──────────────────────────────────────────────────────────
    import uuid
    emails = [
        ("e_001", "priya.sharma@infosys.com", "Cloud Migration Proposal - NexCRM", "Hi Priya,\n\nPlease find attached the cloud migration proposal as discussed. Looking forward to your feedback.\n\nBest regards", str(uuid.uuid4()), 3, now - timedelta(hours=5), False, None, "sent", "c_001", "Proposal"),
        ("e_002", "rahul.mehta@tcs.com", "Revised Enterprise License Pricing", "Hi Rahul,\n\nAs promised, here are the revised pricing tiers with the volume discounts. Let me know if you have questions.\n\nRegards", str(uuid.uuid4()), 1, now - timedelta(hours=2), False, None, "sent", "c_002", "Follow-up"),
        ("e_003", "ananya.r@wipro.com", "AI Integration Demo Invite", "Hi Ananya,\n\nGreat meeting you at TechSummit! Would love to schedule a demo of our AI integration capabilities. How does next Thursday work?\n\nBest", str(uuid.uuid4()), 0, None, False, None, "sent", "c_003", "Meeting Request"),
        ("e_004", "vikram.desai@zoho.com", "CRM Migration Timeline", "Hi Vikram,\n\nHere's the preliminary migration timeline we discussed. Phase 1 covers data migration and should take about 4 weeks.\n\nCheers", str(uuid.uuid4()), 5, now - timedelta(minutes=30), False, None, "sent", "c_004", "Follow-up"),
        ("e_005", "meera.nair@freshworks.com", "API Integration Specifications", "Hi Meera,\n\nAttached are the API specs for the bidirectional sync. Let's schedule a technical deep-dive with your engineering team.\n\nBest", str(uuid.uuid4()), 2, now - timedelta(hours=1), False, None, "sent", "c_005", "Proposal"),
        ("e_006", "me@nexcrm.com", "Re: POS System - Offline Mode", "Hi,\n\nThank you for the documentation on offline-first architecture. We've reviewed it and it looks great for our tier-2/3 stores.\n\nCan we schedule a call this week to discuss implementation?\n\nRegards,\nArjun Patel", None, 0, None, True, now - timedelta(hours=3), "received", "c_006", "Follow-up"),
        ("e_007", "kavitha.i@hcltech.com", "RFP Response - Analytics Platform", "Hi Kavitha,\n\nPlease find our formal RFP response attached. We've addressed all requirements including SOC2 compliance details.\n\nBest regards", str(uuid.uuid4()), 4, now - timedelta(hours=1, minutes=20), False, None, "sent", "c_007", "Proposal"),
        ("e_008", "me@nexcrm.com", "Onboarding Feedback - Razorpay", "Hi Team,\n\nThe onboarding went smoothly. Just a couple of suggestions:\n1. Dashboard load time could be faster\n2. Would love bulk import for historical data\n\nCheers,\nSanjay", None, 0, None, False, None, "received", "c_008", "Check-in"),
        ("e_009", "deepika.j@swiggy.com", "Logistics Optimization - Case Studies", "Hi Deepika,\n\nAttached are two relevant case studies from similar high-volume logistics companies. Happy to discuss further.\n\nBest", str(uuid.uuid4()), 0, None, False, None, "sent", "c_009", "Cold Outreach"),
        ("e_010", "me@nexcrm.com", "LMS Integration Questions", "Hello,\n\nWe have a few technical questions about the proposed architecture:\n- How does real-time sync work?\n- What is the expected latency?\n- Can we customize the analytics dashboard?\n\nRegards,\nRohan Kapoor", None, 0, None, False, None, "received", "c_010", "Follow-up"),
    ]
    for e in emails:
        sent = now - timedelta(days=12 - emails.index(e), hours=emails.index(e) * 2)
        await conn.execute(
            'INSERT INTO emails (id, to_email, subject, body, "trackingId", "openCount", "lastOpenedAt", "isRead", "readAt", direction, "contactId", type, "sentAt") VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)',
            *e, sent,
        )
    print("[OK] 10 emails inserted (with tracking data)")

    # ── Activity ────────────────────────────────────────────────────────
    activities = [
        ("deal", "New deal created: Infosys Cloud Migration — ₹4.5L", "green"),
        ("contact", "Priya Sharma added as a new contact", "blue"),
        ("email", "Proposal sent to priya.sharma@infosys.com", "purple"),
        ("task", "Task completed: Onboarding call with Razorpay team", "green"),
        ("deal", "Deal stage updated: Reliance POS Rollout → Negotiation", "orange"),
        ("note", "Meeting notes added for TCS License Discussion", "blue"),
        ("deal", "Deal won: Razorpay Dashboard — ₹95K", "green"),
        ("contact", "Deepika Joshi added as a new contact", "blue"),
        ("task", "New task: Follow up with Priya on cloud proposal", "yellow"),
        ("email", "RFP response sent to kavitha.i@hcltech.com", "purple"),
    ]
    for i, a in enumerate(activities):
        t = now - timedelta(hours=len(activities) - i, minutes=i * 7)
        await conn.execute(
            "INSERT INTO activity (type, text, color, time) VALUES ($1,$2,$3,$4)",
            *a, t,
        )
    print("[OK] 10 activity entries inserted")

    print("\nSeed complete! All tables populated with realistic data.")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
