from googletrans import Translator as GTranslator
import google.generativeai as genai

class Translator:
    translator = GTranslator()
    
    # 🔑 Paste your Gemini API key
    genai.configure(api_key="")  # Replace with your real key

    # List available models
    # models = genai.list_models()
    # for model in models:
    #     print(model.name)
    # 🧠 Load Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")

    @staticmethod
    def translate_to_darija(prompt):
        """        Translate text from or to Moroccan Darija Arabic using Gemini model.
        Args:
            prompt (str): Custom prompt for translation.
        Returns:
            str: Translated text in Moroccan Darija Arabic or other language.
        """
        response = Translator.model.generate_content(prompt)
        return response.text.strip()

    @staticmethod
    def get_available_languages():
        try:
            languages = Translator.translator.languages
            return {lang.code: lang.name for lang in languages}
        except Exception as e:
            return f"Erreur: {e}"
        
    @staticmethod
    def translate(text, source_language, target_language):
        try:
            result = Translator.translator.translate(text, src=source_language, dest=target_language)
            return result.text
        except Exception as e:
            return f"Erreur: {e}"