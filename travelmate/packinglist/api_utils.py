from openai import OpenAI
import json
import requests
from dotenv import load_dotenv
import os


def configure():
    load_dotenv()


def is_api_key_valid(api_key):
    """Check if the API key is valid by making a test request"""
    try:
        test_client = OpenAI(
            base_url="https://api.deepseek.com",
            api_key=api_key,
        )
        # Make a very small test request
        test_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=5,
        )
        return True
    except Exception as e:
        print(f"API key validation failed: {str(e)}")
        return False


configure()
client = None
API_KEY = os.getenv("api_key")
if API_KEY and is_api_key_valid(API_KEY):
    client = OpenAI(
        base_url="https://api.deepseek.com",
        api_key=API_KEY,
    )


def get_ai_suggestions(location, start, end, count, existing_items, activities, considerations):
    """Fetch packing suggestions from DeepSeek API"""
    if not client:
        return {
            "suggestions": [
                {
                    "title": "Heavy Winter Coat",
                    "description": "A thick, insulated coat to protect against Boston's cold December temperatures",
                    "weather_consideration": "Essential for temperatures often below freezing",
                },
                {
                    "title": "Warm Gloves and Scarf",
                    "description": "Accessories to keep hands and neck warm in chilly weather",
                    "weather_consideration": "Necessary to prevent frostbite and keep comfortable outdoors",
                },
                {
                    "title": "Waterproof Boots",
                    "description": "Boots designed to keep feet dry and warm during snow or rain",
                    "weather_consideration": "Important for navigating snowy or wet sidewalks",
                },
                {
                    "title": "Layered Clothing",
                    "description": "Multiple layers of clothing to easily adjust to varying indoor and outdoor temperatures",
                    "weather_consideration": "Allows for flexibility in Boston's unpredictable winter weather",
                },
                {
                    "title": "Portable Umbrella",
                    "description": "A compact umbrella for sudden rain or snow showers",
                    "weather_consideration": "Useful for unexpected precipitation common in December",
                },
            ]
        }
    existing_names = [item["name"].lower() for item in existing_items]
    prompt = f"""
        Generate {count} essential packing items for a trip to {location} from the day {start} to end {end}.
        TRIP DETAILS:
        - Destination: {location}
        - Weather: Weather from {start} to {end}
        - Activities: {activities}
        - Special Considerations: {considerations}
        
        IMPORTANT RULES:
        1. NEVER suggest these existing items: {', '.join(existing_names)}
        2. If suggesting similar items, make them meaningfully different
        3. Prioritize items needed for these activities: {activities}
        4. Account for these special considerations: {considerations}
        
        ITEM REQUIREMENTS:
        - Must be essential for either the destination, duration, or planned activities
        - Include weather-specific items when relevant
        - Make distinct from existing items
        
        For each item, provide:
        - A short title
        - A detailed description (1 sentence)
        - A weather consideration (if applicable)

        Format as JSON with keys 'title' and 'description'.
        Example:
    {{
        "suggestions": [
            {{
                "title": "Waterproof Jacket",
                "description": "Lightweight raincoat for unexpected showers"
            }}
        ]
    }}
        """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
