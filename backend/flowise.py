import requests

FLOWISE_MEMORY_URL = "http://localhost:3000/api/v1/prediction/291a36f1-2421-492c-ad35-44cdc0eb2f6b"
FLOWISE_NUTRITION_URL = "http://localhost:3000/api/v1/prediction/1491add0-942d-48dd-866a-cfc2eb503c69"

def get_flowise_memory(user_message: str) -> str:
    """Query Flowise to get memory context for the current message."""
    try:
        context_query = f"Based on our conversation history, what do you remember that is relevant to this: {user_message}"
        response = requests.post(FLOWISE_MEMORY_URL, json={"question": context_query})
        data = response.json()
        memory = data.get("text", "")
        if memory:
            return f"\n\nFlowise Memory Context:\n{memory}"
        return ""
    except Exception as e:
        return ""

def query_nutrition_architect(message: str, image_data: str = None, image_media_type: str = None) -> str:
    """Send a message to the Nutrition Architect pipeline."""
    try:
        payload = {"question": message}
        if image_data and image_media_type:
            payload["uploads"] = [
                {
                    "data": f"data:{image_media_type};base64,{image_data}",
                    "type": "file",
                    "name": "image",
                    "mime": image_media_type
                }
            ]
        response = requests.post(FLOWISE_NUTRITION_URL, json=payload)
        data = response.json()
        return data.get("text", "Sorry, I couldn't get a response from the Nutrition Architect.")
    except Exception as e:
        return f"Nutrition Architect error: {str(e)}"