# NovaSmart Fleet Delivery Ops - Next-Gen Autonomous AI Fleet Engine

[![Google Agent Development Kit](https://img.shields.io/badge/ADK-1.1.0-blue.svg)](https://cloud.google.com/vertex-ai)
[![Deployment Target](https://img.shields.io/badge/Deployment-Agent%20Runtime-green.svg)](https://cloud.google.com/vertex-ai)
[![A2UI Enabled](https://img.shields.io/badge/A2UI-Enabled-orange.svg)](https://cloud.google.com/vertex-ai)
[![Vertex AI Memory Bank](https://img.shields.io/badge/Memory-Vertex%20Memory%20Bank-purple.svg)](https://cloud.google.com/vertex-ai)

NovaSmart Fleet Delivery Ops is Google's next-generation autonomous AI dark-store logistics dispatcher, rider telemetry monitor, and multi-modal media engine. Built on the **Google Agent Development Kit (ADK)** and deployed on **Vertex AI Agent Runtime**, NovaSmart re-imagines hyper-local delivery from the ground up.

![NovaSmart Fleet Delivery Ops Demo](demo.gif)

---

## 🌟 The CEO Vision: Why NovaSmart Disrupts Legacy Tracking Platforms

Traditional delivery and tracking systems (e.g. legacy courier portals, basic GPS dots, passive text bots) suffer from critical limitations: static 2D maps, generic ETA calculations, zero weather-safety adaptation, and rigid canned responses.

**NovaSmart Fleet Ops introduces a revolutionary AI-native paradigm:**

| Capability | Legacy Tracking Platforms (Uber Eats, DoorDash, FedEx) | NovaSmart Fleet Ops (Google AI Agent Engine) |
| :--- | :--- | :--- |
| **Interface** | Passive text chat or rigid static web forms | **Dynamic A2UI Cards** with native video players, interactive action buttons, and live route maps |
| **Generative Media** | Generic stock photos / no media generation | **Generative 3D Promo Videos** (Google Omni Model) & **Package Proof-of-Delivery Images** (Imagen 3) |
| **Weather Safety** | Static GPS estimates ignoring weather alerts | **Real-Time Weather Radar** (National Weather Service REST API) for rider safety rerouting |
| **Memory & Context** | Resets context every turn / session | **Vertex AI Memory Bank** retaining dispatcher preferences and hub notes across sessions |
| **Eco-Sustainability** | Unknown carbon emissions | **Real-time CO2 Footprint Estimator** and EV zero-emission vehicle routing |
| **Batch Dispatch** | Manual or rule-based dispatching | **Autonomous Dark-Store Batch Dispatch** optimizing courier telemetry and stock levels in real time |

---

## 🚀 Core Features & Capabilities

### 📦 1. Order & Courier Telemetry (Google Cloud Firestore)
- **Real-Time Order Querying**: Fetches live order states (`pending`, `assigned`, `in_transit`, `delivered`) and item details.
- **Rider Telemetry HUD**: Monitors active rider battery levels, vehicle types (E-Bikes, Cargo Scooters, EV Pods), GPS coordinates, and current transit speeds.
- **Batch Dispatch Optimization**: Automatically pairs pending dark-store orders with available couriers at fulfillment hubs.

### 📊 2. AI Fleet Analytics & Rider Safety
- **Battery & Performance HUD**: Evaluates rider battery health across the fleet, raising alerts for couriers with low charge (<50%) and generating automated battery swap schedules.

### 🌱 3. Carbon Footprint & Eco-Routing Estimator
- **Zero-Emission Tracking**: Calculates transit duration, carbon emissions (grams CO2e), and CO2 saved compared to internal combustion delivery vans.

### 🏪 4. Dark-Store Inventory Replenishment
- **Stock Alert Radar**: Monitors dark-store item inventory (Matcha Latte, Avocado Bowl, Organic Cold Brew) and triggers automated reorders for low-stock SKUs.

### 🌧️ 5. Real-Time Route Weather Safety (National Weather Service API)
- **Active Corridor Advisories**: Queries the NWS REST API (`api.weather.gov`) for precipitation alerts, wind advisories, and rider safety warnings.

### 🗺️ 6. Location Intelligence (Google Maps Platform APIs)
- **Geocoding & Places (New)**: Converts street addresses to spatial coordinates and searches nearby fueling/maintenance hubs.
- **Static Maps API**: Generates visual route maps highlighting hub markers and drop-off destinations.

### 🎥 7. 3D Item Promo Video Generation (Google Omni Model)
- **Generative Media**: Calls Google's Omni Model (`gemini-omni-flash-preview` / `veo-3.1-lite-generate-001`) in the `global` region to generate 3D item promo videos, uploaded directly to public Cloud Storage (`velocity-track-media-9707`).

### 📸 8. Package Proof-of-Delivery Previews (Vertex AI Imagen 3)
- **AI Item Previews**: Uses Imagen 3 (`imagen-3.0-generate-002`) to render photorealistic package content preview images.

---

## 🛠️ Architecture & Google Cloud Tech Stack

```
[ Web Browser / Portal ]
        │
        ▼ (FastAPI Proxy / A2A Protocol)
[ Vertex AI Agent Runtime ] ──► [ Vertex AI Memory Bank ]
        │
        ├──► [ Google Cloud Firestore ] (Orders & Couriers)
        ├──► [ Google Cloud Storage ] (velocity-track-media-9707)
        ├──► [ Google Maps Platform ] (Geocoding, Places, Static Maps)
        ├──► [ National Weather Service API ] (Route Radar)
        ├──► [ Vertex AI Imagen 3 ] (POD Images)
        └──► [ Google Omni Model ] (gemini-omni-flash-preview Video)
```

---

## 💻 Local Setup & Execution

### 1. Environment Setup
```bash
cp .env.example .env
# Add your Google Maps API Key to .env:
# GOOGLE_MAPS_API_KEY=your_key_here
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Seed Database
```bash
uv run python seed_firestore_orders.py
```

### 4. Run Agent Developer UI
```bash
adk web app
```

### 5. Run Web Portal Proxy
```bash
uv run python frontend/main.py
```
Open your browser at the local server address output by the console.

---

## ☁️ Deployment Commands

### Deploy Agent Engine
```bash
agents-cli deploy --project <YOUR_PROJECT_ID> --no-confirm-project --update-env-vars "GOOGLE_MAPS_API_KEY=<YOUR_API_KEY>"
```

### Deploy Web Portal to Cloud Run
```bash
gcloud run deploy fleet-delivery-frontend --source frontend/ --region us-east1 --allow-unauthenticated
```
