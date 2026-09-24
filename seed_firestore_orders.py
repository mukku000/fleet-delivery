import os
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-02-e73129932fd9"

db = firestore.Client(project=PROJECT_ID)

customer_names = [
    "Sarah Jenkins", "Alex Rivera", "David Chen", "Emily Watson", "Marcus Vance",
    "Elena Rostova", "Liam O'Connor", "Aisha Khan", "Carlos Mendez", "Chloe Bennett",
    "Kenji Sato", "Priya Patel", "Hannah Abbott", "Gabriel Silva", "Nora Al-Mansoor"
]

addresses = [
    "120 Market St, San Francisco, CA", "742 Evergreen Terrace, Springfield", "88 Colin P Kelly Jr St, San Francisco, CA",
    "500 Howard St, San Francisco, CA", "350 Mission St, San Francisco, CA", "100 California St, San Francisco, CA",
    "201 Spear St, San Francisco, CA", "1 First St, San Francisco, CA", "101 Montgomery St, San Francisco, CA",
    "600 Montgomery St, San Francisco, CA"
]

hubs = [
    "Downtown Express Hub #1", "Westside Logistics Center", "Bay Area Hub North",
    "SoMa Dark Store #4", "Financial District Dispatch"
]

couriers = [
    "Courier CR-502 (Carlos)", "Courier CR-304 (Maya)", "Courier CR-108 (Leo)",
    "Courier CR-712 (Aria)", "Courier CR-220 (Sam)", "Courier CR-419 (Devon)"
]

statuses = ["Pending", "Assigned", "In Transit", "Delivered"]

item_pools = [
    ["Organic Almond Milk", "Artisanal Sourdough Bread", "Cold Brew Coffee 4-Pack"],
    ["Medical First Aid Kit", "Hydration Electrolyte Pack", "Energy Bars"],
    ["Fresh Avocado 3-Pack", "Greek Yogurt 32oz", "Organic Bananas"],
    ["Wireless Charging Pad", "USB-C Braided Cable 6ft", "Noise Canceling Earbuds"],
    ["Gourmet Dark Chocolate", "Matcha Latte Mix", "Sparkling Spring Water 6-Pack"]
]

print("Seeding 100 express orders into Firestore collection 'express_orders'...")

batch = db.batch()
count = 0

for i in range(100, 200):
    order_id = f"ORD-{i}"
    doc_ref = db.collection("express_orders").document(order_id)
    
    order_data = {
        "order_id": order_id,
        "customer_name": customer_names[i % len(customer_names)],
        "delivery_address": addresses[i % len(addresses)],
        "hub": hubs[i % len(hubs)],
        "courier_name": couriers[i % len(couriers)],
        "status": statuses[i % len(statuses)],
        "items": item_pools[i % len(item_pools)],
        "estimated_delivery": f"{(i % 30) + 10} mins",
        "created_at": "2026-09-24T10:00:00Z"
    }
    
    batch.set(doc_ref, order_data)
    count += 1
    
    if count % 20 == 0:
        batch.commit()
        batch = db.batch()

batch.commit()
print(f"Successfully seeded {count} express orders (ORD-100 through ORD-199) into Firestore!")
