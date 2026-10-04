from utils import Logger
import openai


class LLM:
    def __init__(self, provider_config = None):
        self.provider = provider_config.get("provider") if provider_config else None
        self.base_url = provider_config.get("base_url") if provider_config else None
        self.virtual_key = provider_config.get("virtual_key") if provider_config else None
        self.model_name = provider_config.get("model_name") if provider_config else None

        if not self.base_url or not self.virtual_key:
            raise ValueError("Both 'base_url' and 'virtual_key' must be provided in the provider_config.")

        self.logger = Logger(name="LLM")
        self.logger.log("LLM initialized.")
        self.logger.log(f"Base URL: {self.base_url}")
        self.logger.log(f"Provider: {self.provider}")
        self.logger.log(f"Model Name: {self.model_name}")

        self.client = self._create_client()

    def _create_client(self):
        # Placeholder for creating a client based on the provider
        if self.provider == "llmlite":
            client = openai.OpenAI(api_key=self.virtual_key, base_url=self.base_url)
            return client
        elif self.provider == "ollama":
            client = openai.OpenAI(api_key=self.virtual_key, base_url=self.base_url)
            return client
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate(self, prompt: str) -> str:
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
        ).choices[0].message.content

if __name__ == "__main__":
    # Example usage
    provider_config = {
        "provider": "llmlite",
        "base_url": "http://localhost:4000",
        "virtual_key": "",
        "model_name": "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    }

    ollama_provider_config = {
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1",
        "virtual_key": "ollama",
        "model_name": "qwen2.5:7b"
    }

    llmlite_ollama_provider_config = {
        "provider": "llmlite",
        "base_url": "http://localhost:4000",
        "virtual_key": "",
        "model_name": "qwen2.5:7b"
    }

    llm = LLM(provider_config=llmlite_ollama_provider_config)
    response = llm.generate("Hello, how are you?")
    print(response)

        