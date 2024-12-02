import os
import json
from tqdm import tqdm

# ...existing code...

def list_first_level_subfolders(directory):
    subfolders = [f.path for f in os.scandir(directory) if f.is_dir()]
    return subfolders

def convert_json_to_jsonl(json_file, jsonl_file):
    with open(json_file, "r") as f:
        data = json.load(f)
    with open(jsonl_file, "w") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")

# ...existing code...

if __name__ == "__main__":
    # ...existing code...
    output_directory = "CodeS2/CodeS/validation/outputs-test"
    subfolders = list_first_level_subfolders(output_directory)
    for folder in subfolders:
        print(folder)
        for file_name in os.listdir(folder):
            if file_name.endswith(".json"):
                json_file = os.path.join(folder, file_name)
                jsonl_file = os.path.join(folder, file_name + ".jsonl")
                convert_json_to_jsonl(json_file, jsonl_file)
    # ...existing code...
