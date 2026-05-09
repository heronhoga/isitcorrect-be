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
        - No language other than English

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
        
        if language != English, return error:
        {{
            "error": "Only English text is supported"
        }}

        Input:
        {text}

        Output:
        """