from openai import OpenAI
import json

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  model="deepseek/deepseek-r1-zero:free",
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
        model="deepseek/deepseek-r1-zero:free",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content

print(get_ai_suggestions("Boston", "December"))

try:
    test = json.loads(get_ai_suggestions("Boston", "December"))
except json.JSONDecodeError as e:
    test = "Failed"
    print(f"Error decoding JSON: {e}")
print(test)