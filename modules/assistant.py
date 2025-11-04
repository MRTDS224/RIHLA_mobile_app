from google.generativeai import configure as genai_configure
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os
from dotenv import load_dotenv


class Assistant:
    """An AI assistant that can help with various tasks."""
    
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv("API_GENIA_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    def __init__(self):
        self.name = "Assistant"
        self.description = "An AI assistant that can help with various tasks."
        self.version = "1.0.0"

    def greet(self):
        return f"Hello, I am {self.name}. How can I assist you today?"
    
    @staticmethod
    def get_response(prompt):
        """Generates a response based on the provided prompt."""
        try:
            response = Assistant.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"An error occurred while generating a response: {str(e)}"
