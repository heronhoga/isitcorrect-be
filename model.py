import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class HFClient:
    def __init__(self, model_name="ibm-granite/granite-4.1-3b"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )

    def generate(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.0,
            do_sample=False
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


class GrammarModel:
    def __init__(self, client: HFClient):
        self.client = client

    def check(self, text: str) -> dict:
        prompt = self._build_prompt(text)

        raw = self.client.generate(prompt)

        parsed = self._parse(raw)

        if parsed:
            return parsed

        # retry once if parsing fails
        raw = self.client.generate(prompt)
        parsed = self._parse(raw)

        return parsed or {"error": "Invalid model response"}

    def _build_prompt(self, text):
        return f"""
        You are a grammar checker.

        Rules:
        - Fix grammar only
        - Do not change meaning
        - Return ONLY valid JSON

        Format:
        {{
        "corrected": "...",
        "issues": [
            {{"original": "...", "fix": "...", "reason": "..."}}
        ]
        }}

        Text: {text}
        """

    def _parse(self, raw: str):
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            json_str = raw[start:end]

            return json.loads(json_str)
        except Exception:
            return None