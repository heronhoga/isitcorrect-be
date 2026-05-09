def format_prompt(text: str) -> str:
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