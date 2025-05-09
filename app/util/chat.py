import os
import google.generativeai as genai

class Chat:
    def __init__(self):
        genai.configure(api_key=os.getenv('GENAI_API_KEY'))
        model = genai.GenerativeModel(model_name=os.getenv('GENAI_MODEL_NAME'))
        self.chat = model.start_chat()

    def send_message(self, message):
        response = self.chat.send_message(message)
        return response.text
