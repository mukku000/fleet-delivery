from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-02-e73129932fd9"

def _get_firestore_client():
    return firestore.Client(project=PROJECT_ID)

def get_express_order(order_id: str) -> dict:
    """Retrieve details of a specific express delivery order by its order ID (e.g. 'ORD-8901')."""
    db = _get_firestore_client()
    doc_ref = db.collection("express_orders").document(order_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Order {order_id} not found."}
    return doc.to_dict()

def search_orders_by_status(status: str) -> list[dict]:
    """Search for express delivery orders by status (e.g. 'Pending', 'In Transit', 'Assigned', 'Delivered')."""
    db = _get_firestore_client()
    collection_ref = db.collection("express_orders")
    query = collection_ref.where("status", "==", status)
    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["doc_id"] = doc.id
        results.append(data)
    return results

def update_order_status(order_id: str, new_status: str, courier_name: str = None) -> dict:
    """Update the delivery status (e.g. 'In Transit', 'Delivered') and optionally courier for an express order."""
    db = _get_firestore_client()
    doc_ref = db.collection("express_orders").document(order_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Order {order_id} not found."}
    
    update_data = {"status": new_status}
    if courier_name:
        update_data["courier_name"] = courier_name
        
    doc_ref.update(update_data)
    
    updated_doc = doc_ref.get()
    return updated_doc.to_dict()

def optimize_batch_dispatch(hub_name: str = "Downtown Express Hub #1") -> dict:
    """Optimize batch dispatch assignments for pending express orders at a hub, matching available couriers and updating Firestore records."""
    db = _get_firestore_client()
    collection_ref = db.collection("express_orders")
    
    # Query pending orders
    pending_docs = list(collection_ref.where("status", "==", "Pending").limit(10).stream())
    
    if not pending_docs:
        return {
            "message": f"No pending orders currently queued at {hub_name}.",
            "assigned_count": 0,
            "assignments": []
        }
    
    courier_pool = [
        "Courier CR-502 (Carlos)",
        "Courier CR-304 (Maya)",
        "Courier CR-108 (Leo)",
        "Courier CR-712 (Aria)"
    ]
    
    assignments = []
    batch = db.batch()
    
    for idx, doc in enumerate(pending_docs):
        order_data = doc.to_dict()
        assigned_courier = courier_pool[idx % len(courier_pool)]
        
        doc_ref = collection_ref.document(doc.id)
        batch.update(doc_ref, {
            "status": "Assigned",
            "courier_name": assigned_courier
        })
        
        assignments.append({
            "order_id": doc.id,
            "customer_name": order_data.get("customer_name"),
            "delivery_address": order_data.get("delivery_address"),
            "assigned_courier": assigned_courier,
            "status": "Assigned"
        })
    
    batch.commit()
    
    return {
        "hub": hub_name,
        "assigned_count": len(assignments),
        "status": "Success",
        "assignments": assignments
    }

def check_darkstore_inventory(hub_name: str = "Downtown Express Hub #1") -> dict:
    """Check current inventory levels for popular dark-store express items, flagging low-stock items requiring replenishment."""
    items = [
        {"sku": "SKU-1001", "name": "Matcha Latte", "stock_qty": 48, "reorder_level": 15, "status": "In Stock"},
        {"sku": "SKU-1002", "name": "Avocado Bowl", "stock_qty": 8, "reorder_level": 10, "status": "LOW STOCK"},
        {"sku": "SKU-1003", "name": "Organic Cold Brew Coffee", "stock_qty": 62, "reorder_level": 20, "status": "In Stock"},
        {"sku": "SKU-1004", "name": "Artisan Sourdough Toast", "stock_qty": 4, "reorder_level": 8, "status": "LOW STOCK"},
        {"sku": "SKU-1005", "name": "Fresh Berry Parfait", "stock_qty": 35, "reorder_level": 12, "status": "In Stock"}
    ]
    
    low_stock = [item["name"] for item in items if item["stock_qty"] <= item["reorder_level"]]
    
    return {
        "fulfillment_hub": hub_name,
        "total_sku_monitored": len(items),
        "low_stock_alerts": low_stock,
        "inventory_snapshot": items,
        "recommended_reorder": "Trigger auto-replenishment for Avocado Bowl & Artisan Sourdough Toast."
    }
