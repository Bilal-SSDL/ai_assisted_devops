#!/usr/bin/env python3

import os
import sys
import google.generativeai as genai

PROMPT = """
ONLY Generate an ideal Dockerfile for {language} with best practices. Do not provide any description
Include:
    - Base Image
    - Installing dependencies
    - Setting working directory
    - Adding source code
    - Running the application
"""


def generate(language):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content(PROMPT.format(language=language))
    return response.text


if __name__ == "__main__":
    language = input("Enter your programming language: ").strip()
    if not language:
        print("Error: language cannot be empty.")
        sys.exit(1)

    dockerfile = generate(language)
    print("\nGenerated Dockerfile:\n")
    print(dockerfile)
