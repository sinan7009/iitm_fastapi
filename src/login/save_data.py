import json
import os
from datetime import date


def ensure_json_file(filename="iitm_data.json"):
    today_str = date.today().strftime("%Y-%m-%d")

    if not os.path.exists(filename):
        data = {"last_update_date": today_str}

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"🆕 Created new JSON file: {filename} (Last update: {today_str})")
        return "created new json file"
    else:
        return f"JSON file already exists: {filename}"


def get_all_json_data(exam_details, cgpa, filename="iitm_data.json"):
    try:
        ensure_json_file()
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("got all the data")
        if data.get("last_update_date") == date.today().strftime("%Y-%m-%d"):
            print("data is upto date")
        else:
            update_json_date(filename, data, exam_details, cgpa)

        return data

    except FileNotFoundError:
        print(f"⚠️ File '{filename}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"⚠️ File '{filename}' is empty or not valid JSON.")
        return {}


def update_json_date(filename, data, exam_details, cgpa):
    data["last_update_date"] = date.today().strftime("%Y-%m-%d")
    data["exam_details"] = exam_details
    data["cgpa"] = cgpa

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return "cgpa and exam details updated "


ensure_json_file("iitm_data.json")
