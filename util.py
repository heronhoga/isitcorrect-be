import json
import langdetect

def is_english(text) -> bool:
    try:
        return langdetect.detect(text) == "en"
    except langdetect.lang_detect_exception.LangDetectException:
        return False
    
def parse_raw_response(raw: str):
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