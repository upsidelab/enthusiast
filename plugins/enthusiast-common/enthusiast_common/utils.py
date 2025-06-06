def prioritize_items(items: list[str], priorities: list[str]):
    items_set = set(items)
    priorities_set = set(priorities)

    result = [p for p in priorities if p in items_set]
    result += [item for item in items if item not in priorities_set]
    return result
