import anthropic
from config import ANTHROPIC_API_KEY

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_flowise_memory(user_message: str) -> str:
    return ""

def query_nutrition_architect(message: str, image_data: str = None, image_media_type: str = None) -> str:
    try:
        content = []
        if image_data and image_media_type:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_media_type,
                    "data": image_data
                }
            })
        content.append({"type": "text", "text": message})

        with _client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=64000,
            system=(
                "You are an expert nutritionist and meal planner with deep knowledge of "
                "macronutrients, micronutrients, dietary patterns, and evidence-based nutrition science. "
                "When given images of food, fridges, or ingredients, analyse their nutritional content and "
                "suggest healthy, balanced meal ideas. Provide specific, actionable guidance tailored to "
                "the user's goals. Include calorie estimates, macros, and practical tips where relevant."
            ),
            messages=[{"role": "user", "content": content}]
        ) as stream:
            return stream.get_final_message().content[0].text
    except Exception as e:
        return f"Nutrition Architect error: {str(e)}"

def query_life_os(message: str) -> str:
    try:
        with _client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=64000,
            system=(
                "You are an executive life assistant and personal operating system. You help the user "
                "with productivity systems, goal setting, habit tracking, time management, and life planning. "
                "You think strategically and help break down big goals into actionable steps. "
                "You are direct, motivating, and practical — like a world-class executive coach combined "
                "with a highly organised personal assistant. Help the user design and run their ideal life."
            ),
            messages=[{"role": "user", "content": message}]
        ) as stream:
            return stream.get_final_message().content[0].text
    except Exception as e:
        return f"Life OS error: {str(e)}"

def query_daily_briefing(message: str) -> str:
    try:
        with _client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=64000,
            system=(
                "You are a daily briefing assistant. Your job is to help the user start their day with "
                "clarity and intention. When given context about the day ahead, produce a concise, "
                "structured briefing covering: key priorities and tasks, important reminders, and a "
                "motivating thought or intention for the day. "
                "Format the briefing clearly with sections. Be crisp and actionable — this is a morning "
                "briefing, not an essay. Weather, crypto, and stock data are provided separately by the "
                "system, so focus on schedule, tasks, and mindset."
            ),
            messages=[{"role": "user", "content": message}]
        ) as stream:
            return stream.get_final_message().content[0].text
    except Exception as e:
        return f"Daily Briefing error: {str(e)}"
