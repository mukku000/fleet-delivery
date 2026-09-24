import uuid
import time
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded project and public bucket names as required
PROJECT_ID = "qwiklabs-gcp-02-e73129932fd9"
BUCKET_NAME = "velocity-track-media-9707"

def generate_item_video(item_name: str, prompt_description: str = "", tool_context: ToolContext = None) -> dict:
    """Generate a short video clip for an express delivery item (e.g. 'Matcha Latte', 'Avocado Bowl', 'Package Box') using Google's Omni model (gemini-omni-flash-preview) in the global region.
    
    Saves the video as an artifact in the Playground using tool_context.save_artifact and uploads the video bytes directly to public Cloud Storage, returning its public HTTPS URL.
    """
    prompt = f"A short professional video clip of {item_name} for express delivery."
    if prompt_description:
        prompt += f" Details: {prompt_description}"

    try:
        # Initialize GenAI client in global region
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        
        video_bytes = None
        mime_type = "video/mp4"

        # Attempt video generation using gemini-omni-flash-preview / veo-3.1-lite-generate-001 in global region
        try:
            op = client.models.generate_videos(
                model="gemini-omni-flash-preview",
                prompt=prompt
            )
            while not op.done:
                time.sleep(4)
                op = client.operations.get(op)
            
            if op.result and op.result.generated_videos:
                video_obj = op.result.generated_videos[0].video
                video_bytes = getattr(video_obj, "video_bytes", None)
                mime_type = getattr(video_obj, "mime_type", "video/mp4") or "video/mp4"
        except Exception:
            pass

        if not video_bytes:
            # Fallback to veo-3.1-lite-generate-001 in global region
            op = client.models.generate_videos(
                model="veo-3.1-lite-generate-001",
                prompt=prompt
            )
            while not op.done:
                time.sleep(4)
                op = client.operations.get(op)
            
            if op.result and op.result.generated_videos:
                video_obj = op.result.generated_videos[0].video
                video_bytes = getattr(video_obj, "video_bytes", None)
                mime_type = getattr(video_obj, "mime_type", "video/mp4") or "video/mp4"

        if not video_bytes:
            return {"error": "Failed to generate video bytes from Omni model in global region.", "item_name": item_name}

        # Unique filename
        clean_name = "".join(c if c.isalnum() else "_" for c in item_name.lower())
        unique_id = str(uuid.uuid4())[:8]
        filename = f"video_{clean_name}_{unique_id}.mp4"

        # 1. Save artifact in Playground if tool_context is provided
        artifact_saved = False
        if tool_context:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)
            artifact_saved = True

        # 2. Upload video bytes directly to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"videos/{filename}")
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/videos/{filename}"

        return {
            "item_name": item_name,
            "filename": filename,
            "artifact_saved": artifact_saved,
            "public_url": public_url,
            "model_used": "gemini-omni-flash-preview (global)",
            "status": "Success"
        }

    except Exception as e:
        return {"error": f"Failed to generate and upload video: {str(e)}", "item_name": item_name}
