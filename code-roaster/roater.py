import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load environment variables (Like dotenv.config() in Node)
load_dotenv()

# 2. Configure the API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No API key found! Check your .env file.")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


def roast_my_code(user_code):
    """
    Sends code to the AI with a specific persona.
    """

    # The "System Prompt" - This sets the behavior/personality
    prompt = f"""
    You are a cynical, sarcastic Senior Software Engineer who has seen too much bad code.
    
    Your task:
    1. Analyze the following code snippet.
    2. Roast the user hard about their variable names, logic, or lack of comments. Be funny but mean.
    3. After the roast, provide the "Correct" optimized version of the code.
    4. Explain the fix briefly (but condescendingly).

    Here is the code:
    {user_code}
    """

    print("\n👀 Senior Dev is looking at your code...\n")

    # 4. Call the API
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: The AI refused to roast you. Reason: {e}"


if __name__ == "__main__":
    # This block runs only if you execute the file directly
    print("🔥 WELCOME TO THE CODE ROASTER 3000 🔥")
    print(
        "Paste your messy code below. Press Ctrl+D (or Ctrl+Z on Windows) followed by Enter to finish:"
    )

    # Read multi-line input
    import sys

    user_input = sys.stdin.read()

    if user_input.strip():
        result = roast_my_code(user_input)
        print("-" * 50)
        print(result)
        print("-" * 50)
    else:
        print("You didn't paste any code! Coward.")
