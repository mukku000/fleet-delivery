# NovaSmart Fleet Delivery Ops Agent

[![Google Agent Development Kit](https://img.shields.io/badge/ADK-1.1.0-blue.svg)](https://cloud.google.com/vertex-ai)
[![Deployment Target](https://img.shields.io/badge/Deployment-Agent%20Runtime-green.svg)](https://cloud.google.com/vertex-ai)
[![A2UI Enabled](https://img.shields.io/badge/A2UI-Enabled-orange.svg)](https://cloud.google.com/vertex-ai)

NovaSmart Fleet Delivery Ops is an enterprise-grade AI agent designed for high-velocity dark-store logistics, rider dispatch, real-time weather safety monitoring, and media generation. Built with the **Google Agent Development Kit (ADK)** and deployed on **Vertex AI Agent Runtime**, it integrates Google Cloud services, Google Maps APIs, and generative media models into a single conversational interface.

![NovaSmart Fleet Delivery Ops Demo](demo.gif)

---

## Key Capabilities & Features

### 📦 1. Order & Courier Logistics (Google Cloud Firestore)
- **Order Retrieval & Status Updates**: Reads and updates live delivery states (`pending`, `assigned`, `in_transit`, `delivered`) in the Firestore `express_orders` collection.
- **Courier Telemetry**: Queries real-time rider status, battery level, speed, and active order counts from the `couriers` collection.
- **Batch Dispatch Optimization**: Automatically pairs pending orders with available couriers at dark-store fulfillment hubs.

### 🌧️ 2. Real-Time Route Weather Monitoring (National Weather Service API)
- **Route Weather & Safety Advisories**: Queries the National Weather Service (`api.weather.gov`) REST API to fetch live weather conditions, precipitation alerts, and rider safety advisories along active delivery corridors.

### 🗺️ 3. Location Intelligence (Google Maps Platform APIs)
- **Geocoding API**: Converts street addresses into geographic coordinates (`latitude`, `longitude`).
- **Places API (New)**: Searches nearby places (e.g., fuel stations, maintenance hubs, dark stores) using spatial proximity queries.
- **Static Maps API**: Generates visual route maps showing hub locations and delivery drop-off markers.

### 🧠 4. Persistent Memory (Vertex AI Memory Bank)
- **Cross-Session Fact Persistence**: Integrates Vertex AI Memory Bank (`PreloadMemoryTool` and callback hooks) to remember user preferences, frequent fulfillment hubs, and dispatcher notes across sessions.

### 📸 5. AI Package Preview Generation (Vertex AI Imagen 3)
- **Proof of Delivery / Item Previews**: Uses Imagen 3 (`imagen-3.0-generate-002`) to generate photorealistic package content preview images.
- **Cloud Storage Integration**: Uploads raw binary image assets directly to Google Cloud Storage (`velocity-track-media-9707`) and returns public HTTPS URLs.

### 🎥 6. 3D Item Promo Video Generation (Google Omni Model)
- **Generative Item Videos**: Calls Google's Omni Model (`gemini-omni-flash-preview` / `veo-3.1-lite-generate-001`) in the `global` region to produce short item promo videos.
- **Playground Artifacts & GCS Upload**: Saves video artifacts via ADK `ToolContext.save_artifact` for the Playground panel and uploads public MP4 files to Cloud Storage.

### 🎨 7. Rich Interactive UI (A2UI Protocol)
- **Native Card Components**: Emits structured A2UI surface components (`Card`, `Column`, `Row`, `Text`, `Image`, `Video`, `Button`).
- **HTML5 Media Player**: Custom web frontend natively renders static route maps and plays HTML5 MP4 videos directly inside the chat interface.

### 💻 8. Code Sandbox Execution
- **Dynamic Python Sandbox**: Runs `AgentEngineSandboxCodeExecutor` for complex routing algorithms, distance matrix calculations, and analytics math.

---

## Tech Stack & Architecture

- **Framework**: Google Agent Development Kit (ADK `v1.1.0`)
- **Language**: Python 3.13 / 3.14 (`uv` package manager)
- **Database**: Google Cloud Firestore
- **Storage**: Google Cloud Storage (`velocity-track-media-9707`)
- **Memory**: Vertex AI Memory Bank
- **Generative Models**:
  - Reasoning: `gemini-2.5-flash`
  - Image: `imagen-3.0-generate-002`
  - Video: `gemini-omni-flash-preview` / `veo-3.1-lite-generate-001` (Global Region)
- **Deployment**: Vertex AI Agent Runtime (`agents-cli`)

---

## Local Development & Setup

### 1. Environment Configuration
Copy `.env.example` to `.env` and set your Google Maps API Key:
```bash
cp .env.example .env
```
Ensure your `.env` contains:
```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### 2. Install Dependencies
Using `uv`:
```bash
uv sync
```

### 3. Seed Firestore Database
Populate test orders and courier records:
```bash
uv run python seed_firestore_orders.py
```

### 4. Run Agent Locally (ADK Web)
Launch the interactive ADK Web developer interface:
```bash
adk web app
```

### 5. Run Custom Web Frontend & Proxy
Start the FastAPI proxy server with built-in A2UI mini-renderer:
```bash
uv run python frontend/main.py
```
Open your browser and navigate to the port output by the console.

---

## Deployment Instructions

### Deploy Agent to Vertex AI Agent Runtime
```bash
agents-cli deploy --project <YOUR_PROJECT_ID> --no-confirm-project --update-env-vars "GOOGLE_MAPS_API_KEY=<YOUR_API_KEY>"
```

### Deploy Frontend Proxy to Google Cloud Run
```bash
gcloud run deploy fleet-delivery-frontend --source frontend/ --region us-east1 --allow-unauthenticated
```
