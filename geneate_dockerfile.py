#!/usr/bin/env python3

import ollama
import argparse
import sys

PROMPT = """
ONLY Generate an ideal Dockerfile for {language} with best practices. Do not provide any description
Include:
- Base image
- Installing dependencies
- Setting working directory
- Adding source code
- Running the application
- multistage distroless dockerfile
"""

def generate_dockerfile(language, model):
    try:
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': PROMPT.format(language=language)
            }],
            options={"temperature": 0}
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def save_to_file(content, output):
    try:
        with open(output, "w") as f:
            f.write(content)
        print(f"✅ Dockerfile saved to: {output}")
    except Exception as e:
        print(f"Failed to save file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate Dockerfile using Ollama")
    parser.add_argument("language", help="Programming language (e.g., python, node, go)")
    parser.add_argument("-o", "--output", default="Dockerfile", help="Output file (default: Dockerfile)")
    parser.add_argument("-m", "--model", default="llama3.2", help="Ollama model (default: llama3.2)")

    args = parser.parse_args()

    print(f"⚡ Generating Dockerfile for: {args.language} using {args.model}...\n")

    dockerfile = generate_dockerfile(args.language, args.model)

    save_to_file(dockerfile, args.output)

if __name__ == "__main__":
    main()
