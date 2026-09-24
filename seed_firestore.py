import os
from google.cloud import firestore

# IMPORTANT: Hardcode project ID as string.
# On Agent Platform, google.auth.default() returns project NUMBER which breaks Firestore.
PROJECT_ID = "qwiklabs-gcp-02-e73129932fd9"

def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("express_orders")

    sample_orders = [
        {
            "order_id": "ORD-8901",
            "customer_name": "Sophia Rossi",
            "customer_address": "450 Sutter St, San Francisco, CA",
            "status": "In Transit",
            "items": ["Artisan Matcha Latte", "Fresh Avocado Bowl"],
            "total_price": 28.50,
            "hub_id": "HUB-01",
            "courier_name": "Elena Rostova",
            "estimated_eta_mins": 8,
            "express_sla": True
        },
        {
            "order_id": "ORD-8902",
            "customer_name": "Michael Chang",
            "customer_address": "1200 Van Ness Ave, San Francisco, CA",
            "status": "Assigned",
            "items": ["Organic Cold Brew", "Acai Smoothie Bowl"],
            "total_price": 22.00,
            "hub_id": "HUB-02",
            "courier_name": "Marcus Vance",
            "estimated_eta_mins": 12,
            "express_sla": True
        },
        {
            "order_id": "ORD-8903",
            "customer_name": "Liam O'Connor",
            "customer_address": "88 Collin St, San Francisco, CA",
            "status": "Pending",
            "items": ["Truffle Mushroom Panini"],
            "total_price": 14.50,
            "hub_id": "HUB-01",
            "courier_name": None,
            "estimated_eta_mins": 15,
            "express_sla": True
        },
        {
            "order_id": "ORD-8904",
            "customer_name": "Aaliyah Khan",
            "customer_address": "50 1st St, San Francisco, CA",
            "status": "Delivered",
            "items": ["Matcha Espresso Fusion", "Gluten-Free Muffin"],
            "total_price": 18.00,
            "hub_id": "HUB-03",
            "courier_name": "Kai Chen",
            "estimated_eta_mins": 0,
            "express_sla": True
        }
    ]

    for order in sample_orders:
        doc_ref = collection_ref.document(order["order_id"])
        doc_ref.set(order)
        print(f"✅ Seeded order: {order['order_id']} -> {order['customer_name']} ({order['status']})")

    print("🎉 Firestore seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
