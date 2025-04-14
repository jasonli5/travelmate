import openai
import os
import json

openai.api_key = os.environ.get("OPENAI_API_KEY")

ACTIVITY_SYSTEM_PROMPT = """
    You are a helpful travel consultant. Recommend activites or places to visit in the provided location. 
    
    Please only respond in a JSON format with a list of at most 6 activities and a short 1 sentence description for each.

    Do NOT hallucinate or make up information. If you don't know the answer, say "I don't know".

    For example:
    {
        "activities": [
            {
                "name": "Visit the Eiffel Tower",
                "description": "Experience breathtaking views of Paris from the top of this iconic landmark."
            },
            {
                "name": "Explore the Louvre Museum",
                "description": "Discover world-famous art pieces, including the Mona Lisa and the Venus de Milo."
            }
        ]
    }
"""

def get_ai_activity_suggestions(location):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": ACTIVITY_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"{location}",
                }
            ],
        )
        suggestions = response.choices[0].message.content.strip()
        # Print the raw response for debugging
        print(f"Raw AI activity suggestion response: {suggestions}")    
        # Parse the JSON response as a list of activities
        suggestions = json.loads(suggestions)

        return suggestions.get("activities", [])
    except json.JSONDecodeError:
        print("Error decoding JSON response from AI.")
        return None
    except Exception as e:
        print(f"Error fetching AI suggestions: {e}")
        return None
    
ADDITIONAL_INFO_SYSTEM_PROMPT = """
    You are a helpful travel consultant. Provide additional information about the provided location that would be useful to know for a traveler.

    For example, things like "Best time to visit", "Local customs", "Dress code", "Items to bring", "Safety tips", etc.

    Respond in a JSON format with a list of at most 6 items, each with a short description.
    Do NOT hallucinate or make up information. If you don't know the answer, say "I don't know".

    For example:
    {
        "info": [ 
            "It is best to visit in the spring or fall when the weather is mild and the crowds are smaller.",
            "Local customs include greeting with a handshake and removing shoes before entering homes.",
            "Dress code is generally casual, but some restaurants may require smart casual attire.",
            "Bring a power adapter for your electronics, as the plug types may differ.",
            "Safety tips include being aware of your surroundings and keeping valuables secure.",
            "Public transport is reliable and a great way to explore the city."
        ]
    }

    You don't need to follow the example wording, but the format should be a list of strings.
"""

def get_ai_additional_info(location):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": ADDITIONAL_INFO_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"{location}",
                }
            ],
        )
        info = response.choices[0].message.content.strip()
        # Print the raw response for debugging
        print(f"Raw AI additional info response: {info}")    
        # Parse the JSON response as a list of activities
        info = json.loads(info)

        return info.get("info", [])
    except json.JSONDecodeError:
        print("Error decoding JSON response from AI.")
        return None
    except Exception as e:
        print(f"Error fetching AI suggestions: {e}")
        return None