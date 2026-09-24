import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded project and bucket names as required
PROJECT_ID = "qwiklabs-gcp-02-e73129932fd9"
BUCKET_NAME = "velocity-track-media-9707"

def generate_item_image(item_name: str, prompt_description: str = "", tool_context: ToolContext = None) -> dict:
    """Generate a visual image/preview for a dark store delivery item or proof-of-delivery (e.g. 'Matcha Latte', 'Avocado Bowl') using gemini-3.1-flash-lite-image in the global region.
    
    Saves the image as an artifact in the Playground and uploads it to public Cloud Storage, returning its public HTTPS URL.
    """
    prompt = f"A professional high-quality studio photo of {item_name} for express delivery."
    if prompt_description:
        prompt += f" Details: {prompt_description}"

    try:
        # Initialize Vertex AI GenAI client in global location
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.inline_data:
                            image_bytes = part.inline_data.data
                            mime_type = part.inline_data.mime_type or "image/jpeg"
                            break

        if not image_bytes:
            return {"error": "Failed to generate image bytes from Gemini model.", "item_name": item_name}

        # Generate unique filename for artifact and GCS object
        clean_item_name = "".join(c if c.isalnum() else "_" for c in item_name.lower())
        unique_id = str(uuid.uuid4())[:8]
        ext = "jpg" if "jpeg" in mime_type else "png"
        filename = f"{clean_item_name}_{unique_id}.{ext}"

        # 1. Save artifact in Playground if tool_context is provided
        artifact_saved = False
        if tool_context:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)
            artifact_saved = True

        # 2. Upload image bytes directly to public GCS bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"items/{filename}")
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/items/{filename}"

        return {
            "item_name": item_name,
            "filename": filename,
            "artifact_saved": artifact_saved,
            "public_url": public_url,
            "status": "Success"
        }

    except Exception as e:
        return {"error": f"Failed to generate and upload image: {str(e)}", "item_name": item_name}
