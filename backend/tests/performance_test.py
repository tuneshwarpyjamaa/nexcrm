from locust import HttpUser, task, between
import json
import random
from datetime import datetime

class CRMUserBehavior(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        # Login and get token
        response = self.client.post("/api/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(3)
    def get_contacts(self):
        """Get contacts list - most common operation"""
        self.client.get("/api/contacts", headers=self.headers)
    
    @task(2)
    def get_deals(self):
        """Get deals list"""
        self.client.get("/api/deals", headers=self.headers)
    
    @task(2)
    def get_tasks(self):
        """Get tasks list"""
        self.client.get("/api/tasks", headers=self.headers)
    
    @task(1)
    def create_contact(self):
        """Create a new contact"""
        contact_data = {
            "name": f"Test User {random.randint(1000, 9999)}",
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "phone": f"+1{random.randint(2000000000, 9999999999)}",
            "company": random.choice(["Acme Corp", "Tech Inc", "Global LLC", "Startup Co"])
        }
        self.client.post("/api/contacts", json=contact_data, headers=self.headers)
    
    @task(1)
    def create_deal(self):
        """Create a new deal"""
        deal_data = {
            "title": f"Deal {random.randint(1000, 9999)}",
            "value": random.uniform(1000, 100000),
            "status": random.choice(["lead", "contacted", "qualified", "proposal", "negotiation", "won", "lost"]),
            "contact_id": f"c_{random.randint(1, 100)}"
        }
        self.client.post("/api/deals", json=deal_data, headers=self.headers)
    
    @task(1)
    def create_task(self):
        """Create a new task"""
        task_data = {
            "title": f"Task {random.randint(1000, 9999)}",
            "description": f"Task description {random.randint(1000, 9999)}",
            "status": random.choice(["pending", "in_progress", "completed"]),
            "priority": random.choice(["low", "medium", "high"]),
            "contact_id": f"c_{random.randint(1, 100)}"
        }
        self.client.post("/api/tasks", json=task_data, headers=self.headers)
    
    @task(1)
    def get_activities(self):
        """Get activities list"""
        self.client.get("/api/activities", headers=self.headers)
    
    @task(1)
    def get_notes(self):
        """Get notes list"""
        self.client.get("/api/notes", headers=self.headers)
    
    @task(1)
    def get_user_settings(self):
        """Get user settings"""
        self.client.get("/api/settings", headers=self.headers)

class AdminUserBehavior(HttpUser):
    wait_time = between(2, 5)
    weight = 1  # Less frequent than regular users
    
    def on_start(self):
        """Admin user login"""
        response = self.client.post("/api/login", json={
            "email": "admin@example.com",
            "password": "adminpassword"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(2)
    def get_all_contacts(self):
        """Admin gets all contacts with pagination"""
        self.client.get("/api/contacts?limit=50&offset=0", headers=self.headers)
    
    @task(1)
    def get_system_health(self):
        """Check system health if endpoint exists"""
        self.client.get("/api/health", headers=self.headers)
    
    @task(1)
    def get_user_subscriptions(self):
        """Get subscription information"""
        self.client.get("/api/subscriptions/me", headers=self.headers)

class StressTestUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Very low wait time for stress testing
    weight = 0.5  # Fewer users but higher frequency
    
    def on_start(self):
        """Quick login for stress testing"""
        response = self.client.post("/api/login", json={
            "email": "stress@example.com",
            "password": "password123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(5)
    def rapid_contact_access(self):
        """Rapidly access contacts"""
        self.client.get("/api/contacts", headers=self.headers)
    
    @task(3)
    def rapid_deal_access(self):
        """Rapidly access deals"""
        self.client.get("/api/deals", headers=self.headers)
    
    @task(2)
    def create_rapid_entities(self):
        """Create entities rapidly"""
        entity_type = random.choice(["contact", "deal", "task"])
        
        if entity_type == "contact":
            data = {
                "name": f"Stress User {random.randint(10000, 99999)}",
                "email": f"stress{random.randint(10000, 99999)}@example.com"
            }
            self.client.post("/api/contacts", json=data, headers=self.headers)
        elif entity_type == "deal":
            data = {
                "title": f"Stress Deal {random.randint(10000, 99999)}",
                "value": random.uniform(5000, 50000),
                "status": "open"
            }
            self.client.post("/api/deals", json=data, headers=self.headers)
        else:
            data = {
                "title": f"Stress Task {random.randint(10000, 99999)}",
                "priority": "high"
            }
            self.client.post("/api/tasks", json=data, headers=self.headers)

class WebsiteUser(HttpUser):
    wait_time = between(2, 4)
    
    @task(3)
    def load_homepage(self):
        """Load the main homepage"""
        self.client.get("/")
    
    @task(2)
    def load_dashboard(self):
        """Load dashboard page"""
        self.client.get("/dashboard.html")
    
    @task(2)
    def load_contacts_page(self):
        """Load contacts page"""
        self.client.get("/contacts.html")
    
    @task(1)
    def load_deals_page(self):
        """Load deals page"""
        self.client.get("/deals.html")
    
    @task(1)
    def load_static_assets(self):
        """Load static CSS and JS files"""
        self.client.get("/css/main.css")
        self.client.get("/js/app.js")

# Test scenarios
class TestScenarios:
    @staticmethod
    def normal_load():
        """Normal load scenario: 50 users over 10 minutes"""
        return {
            "user_classes": [CRMUserBehavior],
            "users": 50,
            "spawn_rate": 5,
            "run_time": "10m"
        }
    
    @staticmethod
    def peak_load():
        """Peak load scenario: 100 users over 5 minutes"""
        return {
            "user_classes": [CRMUserBehavior, AdminUserBehavior],
            "users": 100,
            "spawn_rate": 10,
            "run_time": "5m"
        }
    
    @staticmethod
    def stress_test():
        """Stress test: 200 users over 15 minutes"""
        return {
            "user_classes": [CRMUserBehavior, StressTestUser, AdminUserBehavior],
            "users": 200,
            "spawn_rate": 20,
            "run_time": "15m"
        }
    
    @staticmethod
    def endurance_test():
        """Endurance test: 25 users over 1 hour"""
        return {
            "user_classes": [CRMUserBehavior],
            "users": 25,
            "spawn_rate": 2,
            "run_time": "1h"
        }
    
    @staticmethod
    def website_load():
        """Website load test: 100 users browsing frontend"""
        return {
            "user_classes": [WebsiteUser],
            "users": 100,
            "spawn_rate": 10,
            "run_time": "10m"
        }
