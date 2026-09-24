import os
import json
import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.memory import VertexAiMemoryBankService
from google.genai import types

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from app.a2ui_utils import a2ui_callback

from app.tools.firestore_tools import (
    get_express_order,
    search_orders_by_status,
    update_order_status,
    optimize_batch_dispatch,
    check_darkstore_inventory,
)
from app.tools.courier_tools import check_courier_telemetry, analyze_courier_fleet, estimate_delivery_footprint
from app.tools.weather_tools import get_route_weather
from app.tools.maps_tools import geocode_address, find_nearby_places, generate_route_map
from app.tools.image_tools import generate_item_image
from app.tools.video_tools import generate_item_video

PROJECT_ID = "qwiklabs-gcp-02-e73129932fd9"
MEMORY_BANK_ID = "1957882213638864896"


# Determine Agent Engine resource name from deployment_metadata.json
def _get_code_executor():
    agent_engine_resource_name = None
    metadata_path = os.path.join(os.path.dirname(__file__), "..", "deployment_metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                runtime_id = metadata.get("remote_agent_runtime_id")
                if runtime_id and runtime_id != "None":
                    agent_engine_resource_name = runtime_id
        except Exception:
            pass
            
    if agent_engine_resource_name:
        return AgentEngineSandboxCodeExecutor(agent_engine_resource_name=agent_engine_resource_name)
    return AgentEngineSandboxCodeExecutor()


# Memory Bank Service builder for deployment / runner initialization
def get_memory_service():
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location="us-central1",
        agent_engine_id=MEMORY_BANK_ID,
    )


# Memory callback: save session to Memory Bank at turn end safely
async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass
    return None


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city or query.

    Returns:
        A string with the current time information.
    """
    tz_identifier = "America/Los_Angeles"
    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


# Build A2UI instruction schema
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are VelocityTrack AI, an intelligent agent for express hyperlocal fleet management, order dispatch, "
        "and customer safety. You help dispatchers and customers track active express orders, check courier telemetry, "
        "update order statuses in Firestore, query live delivery route weather, geocode delivery addresses, find nearby places of interest, "
        "generate visual item previews, execute Python code safely in a sandbox, and remember user preferences, dietary restrictions, "
        "and food/medical allergies (e.g. peanuts, gluten, dairy, shellfish, penicillin) across sessions using Memory Bank."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=_get_code_executor(),
    tools=[
        PreloadMemoryTool(),
        get_express_order,
        search_orders_by_status,
        update_order_status,
        optimize_batch_dispatch,
        check_darkstore_inventory,
        check_courier_telemetry,
        analyze_courier_fleet,
        estimate_delivery_footprint,
        get_route_weather,
        geocode_address,
        find_nearby_places,
        generate_route_map,
        generate_item_image,
        generate_item_video,
        get_current_time,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
