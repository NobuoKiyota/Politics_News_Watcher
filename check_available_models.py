import google.generativeai as genai
import os
import config

genai.configure(api_key=config.GEMINI_API_KEY)

print("List of available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  - {m.name}")

print("\nList of available embedding models:")
for m in genai.list_models():
    if 'embedContent' in m.supported_generation_methods:
        print(f"  - {m.name}")
