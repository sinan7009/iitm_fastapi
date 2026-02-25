from google import genai
from google.genai import types
import os

# Ensure your API key is set
client = genai.Client(api_key="AIzaSyBNKJZYl5ja-ZxJbmaxf5ZedvQzqdkopi4")

response = client.models.generate_content(
    model='gemini-2.5-flash-lite',  # Removed the extra 'f'
    contents="what are the three laws of thermodynamics",
    config=types.GenerateContentConfig(
        system_instruction="explain all"
    )
)

# Access the text attribute to see the answer
print(response.text)