import json

def extract_text_from_json(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    def _flatten(obj, prefix="") -> list:
        items = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                items.extend(_flatten(v, f"{prefix}{k}: "))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                items.extend(_flatten(v, f"{prefix}[{i}] "))
        else:
            items.append(f"{prefix}{obj}")
        return items
    return "\n".join(_flatten(data))
