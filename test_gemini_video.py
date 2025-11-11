"""Quick manual script for testing Gemini video description output."""
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-pro")
response = model.generate_content(
    [genai.get_file("agx2br7z6025"), "Describe this video in detail."]
)
print(response.text)
