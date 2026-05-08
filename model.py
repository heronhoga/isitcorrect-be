import json
from huggingface_hub import InferenceClient

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

        prompt = self._build_prompt(text)

        raw = self.client.generate(prompt)

        parsed = self._parse(raw)

        if parsed:
            return parsed

        # retry once
        retry_prompt = (
            prompt +
            "\nRemember: Return ONLY valid JSON."
        )

        raw = self.client.generate(retry_prompt)

        parsed = self._parse(raw)

        if parsed:
            return parsed

        return {
            "error": "Invalid model response",
            "raw": raw
        }

    def _build_prompt(self, text: str) -> str:

        return f"""
    You are a grammar correction engine.

    Rules:
    - Return ONLY valid JSON
    - No markdown
    - No explanation
    - No conversation
    - No extra text
    - No code block

    JSON schema:
    {{
    "corrected": "string",
    "issues": [
        {{
        "original": "string",
        "fix": "string",
        "reason": "string"
        }}
    ]
    }}

    Input:
    {text}

    Output:
    """

    def _parse(self, raw: str):

        try:
            start = raw.find("{")

            if start == -1:
                return None

            brace_count = 0
            end = None

            for i in range(start, len(raw)):

                if raw[i] == "{":
                    brace_count += 1

                elif raw[i] == "}":
                    brace_count -= 1

                    if brace_count == 0:
                        end = i + 1
                        break

            if end is None:
                return None

            json_str = raw[start:end]

            parsed = json.loads(json_str)

            if "corrected" not in parsed:
                return None

            if "issues" not in parsed:
                parsed["issues"] = []

            return parsed

        except Exception:
            return None