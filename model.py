import json
from huggingface_hub import InferenceClient
from prompt import format_prompt
from util import parse_raw_response

class HFClient:
    def __init__(
        self,
        hf_access_token: str,
        model_name: str = (
            "Qwen/Qwen2.5-3B-Instruct:featherless-ai"
        )
    ):

        self.client = InferenceClient(
            api_key=hf_access_token,
        )

        self.model_name = model_name

    def generate(self, prompt: str) -> str:

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=512,
            stop=[
                "\nuser",
                "\nUser",
                "<|eot_id|>",
                "```"
            ]
        )

        content = completion.choices[0].message.content

        print(content)

        return content.strip()

class GrammarModel:
    def __init__(self, client: HFClient):
        self.client = client

    def check(self, text: str) -> dict:

        if not text or not text.strip():
            return {
                "error": "Text is required"
            }

        prompt = format_prompt(text)

        raw = self.client.generate(prompt)

        parsed = parse_raw_response(raw)

        if parsed:
            return parsed

        # retry once
        retry_prompt = (
            prompt +
            "\nRemember: Return ONLY valid JSON."
        )

        raw = self.client.generate(retry_prompt)

        parsed = parse_raw_response(raw)

        if parsed:
            return parsed

        return {
            "error": "Invalid model response",
            "raw": raw
        }

