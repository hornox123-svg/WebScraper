import json


def write_json_report(page_data, filename="report.json"):
    data = sorted(page_data.values(), key = lambda p: p['url'])
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
