import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:3000") as client:
        r = await client.post("/api/register", json={"name": "Test", "email": "net_sub@ex.com", "password": "pass"})
        
        r = await client.post("/api/login", json={"email": "net_sub@ex.com", "password": "pass"})
        token = r.json().get("access_token")
        
        headers = {"Authorization": f"Bearer {token}"}
        r2 = await client.post("/api/subscriptions/subscribe", json={"action": "upgrade", "plan_name": "premium"}, headers=headers)
        print("Status code:", r2.status_code)
        print("Response:", r2.text)

asyncio.run(main())
