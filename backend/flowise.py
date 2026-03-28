import requests

FLOWISE_MEMORY_URL = "http://localhost:3001/api/v1/prediction/291a36f1-2421-492c-ad35-44cdc0eb2f6b"
FLOWISE_NUTRITION_URL = "http://localhost:3001/api/v1/prediction/1491add0-942d-48dd-866a-cfc2eb503c69"
FLOWISE_LIFE_OS_URL = "http://localhost:3001/api/v1/prediction/18ec3890-30ab-43d6-9820-b9bb84537f55"
FLOWISE_DAILY_BRIEFING_URL = "http://localhost:3001/api/v1/prediction/09e72e19-52d5-46e7-a1e7-8e068e51e74f"

def get_flowise_memory(user_message: str) -> str:
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

def query_life_os(message: str) -> str:
    try:
        response = requests.post(FLOWISE_LIFE_OS_URL, json={"question": message})
        data = response.json()
        return data.get("text", "Sorry, I couldn't get a response from the Life OS.")
    except Exception as e:
        return f"Life OS error: {str(e)}"

def query_daily_briefing(message: str) -> str:
    try:
        response = requests.post(FLOWISE_DAILY_BRIEFING_URL, json={"question": message})
        data = response.json()
        return data.get("text", "Sorry, I couldn't get a response from the Daily Briefing.")
    except Exception as e:
        return f"Daily Briefing error: {str(e)}"
