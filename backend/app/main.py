import google.generativeai as genai
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])


# model = genai.GenerativeModel('models/gemini-1.5-flash')
# response = model.generate_content("Hello World! What is the meaning of Life by Hitchhikers Guide to the Galaxy? Give me Shortest Answer Possible.")
# print(response.text)
