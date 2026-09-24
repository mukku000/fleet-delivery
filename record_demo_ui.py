import asyncio
import os
from playwright.async_api import async_playwright

FRONTEND_URL = "https://fleet-delivery-frontend-970704427546.us-east1.run.app"
RECORD_DIR = "/config/Desktop/Session1/fleet-delivery-agent/demo_recordings"

async def record_demo():
    os.makedirs(RECORD_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=RECORD_DIR,
            record_video_size={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        print("1. Opening NovaSmart Fleet Delivery Portal...")
        await page.goto(FRONTEND_URL, wait_until="networkidle")
        await asyncio.sleep(2)

        print("2. Demo 1: Order Lookup (ORD-101)...")
        await page.type("#input", "📦 Check status of express order ORD-101", delay=30)
        await asyncio.sleep(1)
        await page.click("button.send-btn")
        await asyncio.sleep(6)

        print("3. Demo 2: Fleet Analytics & Eco Footprint...")
        await page.type("#input", "📊 Analyze courier fleet performance and eco carbon footprint for ORD-101", delay=30)
        await asyncio.sleep(1)
        await page.click("button.send-btn")
        await asyncio.sleep(6)

        print("4. Demo 3: Live Route Map & Omni Model Video Generation...")
        await page.type("#input", "🗺️ Show delivery route map for ORD-101 and generate a short promo video for Matcha Latte", delay=30)
        await asyncio.sleep(1)
        await page.click("button.send-btn")
        
        # Wait for agent processing & Omni video generation
        await asyncio.sleep(15)

        print("5. Smooth scrolling to highlight maps, analytics cards, and MP4 video player...")
        await page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        await asyncio.sleep(6)

        video_path = await page.video.path()
        await context.close()
        await browser.close()
        print("Raw video recorded at:", video_path)
        return video_path

if __name__ == "__main__":
    asyncio.run(record_demo())
