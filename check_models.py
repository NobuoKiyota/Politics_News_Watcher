import google.generativeai as genai
import config
import os

genai.configure(api_key=config.GEMINI_API_KEY)

print("Listing models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
