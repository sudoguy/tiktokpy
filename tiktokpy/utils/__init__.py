from typing import List


def unique_dicts_by_key(items: List[dict], key: str):
    result = {item[key]: item for item in items}

    return list(result.values())
