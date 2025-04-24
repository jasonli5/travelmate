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
        default_suggestions = [
            {
                "title": "Travel Documents",
                "description": "Passport, ID, tickets, and any necessary visas or permits"
            },
            {
                "title": "Universal Power Adapter",
                "description": "A compact adapter to charge devices in different countries"
            },
            {
                "title": "First Aid Kit",
                "description": "Basic medical supplies like bandages, pain relievers, and antiseptic"
            },
            {
                "title": "Reusable Water Bottle",
                "description": "Eco-friendly and convenient for staying hydrated"
            },
            {
                "title": "Multi-Tool or Swiss Army Knife",
                "description": "Handy for quick fixes, opening packages, or minor repairs"
            },
            {
                "title": "Portable Charger",
                "description": "Backup battery to keep phones and gadgets powered on the go"
            }
        ]

        # Filter out items that already exist
        existing_names = [item["name"].lower() for item in existing_items]
        filtered_suggestions = [
            item for item in default_suggestions
            if item["title"].lower() not in existing_names
        ]

        # Return only the number of requested items (or all available if less than count)
        return {
            "suggestions": filtered_suggestions[:count],
            "used_default": True
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
        5. Make sure at least one of these items accounts for the weather during the time period of the trip ex: if the weather is normally snowy put a winter coat
        
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
