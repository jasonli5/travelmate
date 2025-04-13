from openai import OpenAI
import json
import requests
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()

configure()
client = OpenAI(
  base_url="https://api.deepseek.com",
  api_key= os.getenv('api_key'),
)

completion = client.chat.completions.create(
  model="deepseek-chat",
  messages=[
    {
      "role": "user",
      "content": f"""
        Generate 5 essential packing items for a trip to Boston in the month of December.
        For each item, provide:
        - A short title
        - A detailed description (1 sentence)
        - A weather consideration (if applicable)

       
        Example:
            "suggestions": [
                    "title": "Waterproof Jacket",
                    "description": "Lightweight raincoat for unexpected showers (weather-dependent)"
            ]
        """
    }
  ]
)
def get_ai_suggestions(location, month, count, existing_items):
    """Fetch packing suggestions from DeepSeek API"""
    existing_names = [item['name'].lower() for item in existing_items]
    prompt = f"""
        Generate {count} essential packing items for a trip to {location} in the month of {month}.
        
        IMPORTANT RULES:
        1. NEVER suggest these existing items: {', '.join(existing_names)}
        2. If suggesting similar items, make them meaningfully different
        
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
        response_format={
            'type': 'json_object'
        }
    )

    return json.loads(response.choices[0].message.content)

