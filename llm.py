import anthropic
import openai
class LLMClient: 
    def __init__(self, provider, model):
        self.provider = provider
        self.model = model

        if self.provider == "Anthropic":
            self.client = anthropic.Anthropic()
        elif self.provider == "opneai":
            self.client = openai.OpenAI()
        else:
            self.client = ""

    def chat(self, payload):
        if self.provider == "Anthropic":
            message = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1000,
                temperature=0.5,
                system="You are a world-class poet. Respond only with short poems.",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Why is the ocean salty?"
                            }
                        ]
                    }
                ]
            )
        elif self.provider == "openai":
            
        else