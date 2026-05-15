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
        - No apologies
        - No disclaimers
        - No notes
        - No comments
        - No formatting
        - No lists
        - No emojis
        - No special characters
        - No line breaks
        - No whitespace
        - No indentation
        - No Greetings

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