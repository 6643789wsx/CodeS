"""
This file handles conversations.
"""

import json
import os
import platform
import subprocess

import inquirer

from .render_past_conversation import render_past_conversation
from .utils.display_markdown_message import display_markdown_message
from .utils.local_storage_path import get_storage_path


def conversation_navigator(interpreter):
    print(
        "This feature is not working as of 0.2.0 (The New Computer Update). Please consider submitting a PR to repair it with the new streaming format."
    )
    import time

    time.sleep(5)
    conversations_dir = get_storage_path("conversations")

    display_markdown_message(
        f"""> Conversations are stored in "`{conversations_dir}`".
    
    Select a conversation to resume.
    """
    )

    if not os.path.exists(conversations_dir):
        print(f"No conversations found in {conversations_dir}")
        return None

    # Get list of all JSON files in the directory and sort them by modification time, newest first
    json_files = sorted(
        [f for f in os.listdir(conversations_dir) if f.endswith(".json")],
        key=lambda x: os.path.getmtime(os.path.join(conversations_dir, x)),
        reverse=True,
    )

    # Make a dict that maps reformatted "First few words... (September 23rd)" -> "First_few_words__September_23rd.json" (original file name)
    readable_names_and_filenames = {}
    for filename in json_files:
        name = (
            filename.replace(".json", "")
            .replace(".JSON", "")
            .replace("__", "... (")
            .replace("_", " ")
            + ")"
        )
        readable_names_and_filenames[name] = filename

    # Add the option to open the folder. This doesn't map to a filename, we'll catch it
    readable_names_and_filenames["> Open folder"] = None

    # Use inquirer to let the user select a file
    questions = [
        inquirer.List(
            "name",
            message="",
            choices=readable_names_and_filenames.keys(),
        ),
    ]
    answers = inquirer.prompt(questions)

    # If the user selected to open the folder, do so and return
    if answers["name"] == "> Open folder":
        open_folder(conversations_dir)
        return

    selected_filename = readable_names_and_filenames[answers["name"]]

    # Open the selected file and load the JSON data
    with open(os.path.join(conversations_dir, selected_filename), "r") as f:
        messages = json.load(f)

    # Pass the data into render_past_conversation
    render_past_conversation(messages)

    # Set the interpreter's settings to the loaded messages
    interpreter.messages = messages
    interpreter.conversation_filename = selected_filename

    # Start the chat
    interpreter.chat()


def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.run(["open", path])
    else:
        # Assuming it's Linux
        subprocess.run(["xdg-open", path])
