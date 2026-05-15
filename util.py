import json
import re

def parse_raw_response(raw: str):
    def validate_issue(issue):
        if not isinstance(issue, dict):
            return False

        required_keys = ["original", "fix", "reason"]

        for key in required_keys:
            if key not in issue:
                return False

            if not isinstance(issue[key], str):
                return False

        return True

    def validate(parsed):
        if not isinstance(parsed, dict):
            return None

        # corrected
        if "corrected" not in parsed:
            return None

        if not isinstance(parsed["corrected"], str):
            return None

        # issues
        if "issues" not in parsed:
            parsed["issues"] = []

        if not isinstance(parsed["issues"], list):
            return None

        valid_issues = []

        for issue in parsed["issues"]:
            if validate_issue(issue):
                valid_issues.append(issue)

        parsed["issues"] = valid_issues

        return parsed

    # ==========================================
    # PRIMARY JSON EXTRACTION
    # ==========================================

    try:
        start = raw.find("{")

        if start != -1:
            brace_count = 0
            end = None

            in_string = False
            escape = False

            for i in range(start, len(raw)):
                char = raw[i]

                # escaped chars
                if escape:
                    escape = False
                    continue

                if char == "\\":
                    escape = True
                    continue

                # string state
                if char == '"':
                    in_string = not in_string
                    continue

                # ignore braces inside strings
                if in_string:
                    continue

                if char == "{":
                    brace_count += 1

                elif char == "}":
                    brace_count -= 1

                    if brace_count == 0:
                        end = i + 1
                        break

            if end is not None:
                json_str = raw[start:end]

                parsed = json.loads(json_str)

                validated = validate(parsed)

                if validated:
                    return validated

    except json.JSONDecodeError:
        pass

    # ==========================================
    # REGEX FALLBACK
    # ==========================================

    try:
        patterns = [
            r'\{[\s\S]*?"corrected"[\s\S]*?\}',
            r'\{[\s\S]*?"issues"[\s\S]*?\}',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, raw)

            for match in matches:
                try:
                    parsed = json.loads(match)

                    validated = validate(parsed)

                    if validated:
                        return validated

                except json.JSONDecodeError:
                    continue

    except Exception:
        pass

    # ==========================================
    # LAST RESORT FALLBACK
    # ==========================================

    cleaned = raw.strip()

    if cleaned:
        return {
            "corrected": cleaned,
            "issues": []
        }

    return None