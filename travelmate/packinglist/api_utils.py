from openai import OpenAI
import json
import requests
import creds

client = OpenAI(
  base_url="https://api.deepseek.com",
  api_key=creds.DEEPSEEK_API_KEY,
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
def get_ai_suggestions(location, month):
    """Fetch packing suggestions from DeepSeek API"""
    prompt = f"""
        Generate 5 essential packing items for a trip to {location} in the month of {month}.
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

