import csv
import requests
import json
import os
from datetime import datetime

def get_player_data(player_tag):
    url = f"https://api.clashroyale.com/v1/players/%23{player_tag}"
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer E5jHbGcI0OiJiUzUxMiIsImTpaZkC6IjI0YzQxOGY3LWFhZDYtMDAwYy1hMmRmLTY3YzQzMmM2Y2NhNSJ9.eY3pc3MibOiJiYW50cyIsInF1ZCciOiI5ZDRjbWF2cjpzZWdtZW50YWwifX0.LzlHs-83VFQe9Qp5GW13P03YV6Gja5FQY6DFZOu4znNVXLF6H7J5F_rCgTyGueEOmP5qsXMR5mNBwMWTkF8M5g"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve player data. Status code:", response.status_code)
        print("Response content:", response.content)
        return None


def write_player_data_to_csv_and_json(player_data, csv_filename, json_filename):
    if player_data:
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file, \
                open(json_filename, mode='w', encoding='utf-8') as json_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Attribute", "Name", "Level", "Max Level", "Progress", "Target", "Icon URL"])

            json.dump(player_data, json_file, indent=4)

            for key, value in player_data.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            icon_url = item.get("iconUrls", {}).get("large", "")
                            csv_writer.writerow([key, item.get("name", ""), item.get("level", ""), item.get("maxLevel", ""), item.get("progress", ""), item.get("target", ""), icon_url])
                        else:
                            csv_writer.writerow([key, "", "", "", "", "", ""])
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, dict):
                            icon_url = v.get("iconUrls", {}).get("large", "")
                            csv_writer.writerow([key, v.get("name", ""), v.get("level", ""), v.get("maxLevel", ""), v.get("progress", ""), v.get("target", ""), icon_url])
                        else:
                            csv_writer.writerow([key, "", "", "", "", "", ""])
                else:
                    csv_writer.writerow([key, "", "", "", "", "", value])

        print("Player data has been written to", csv_filename)
    else:
        print("No player data available.")


def save_player_data(player_data, player_tag):
    username = player_data.get("name", "UnknownUser")
    user_folder = os.path.join("data", username)
    os.makedirs(user_folder, exist_ok=True)

    # Add date and time to the folder name
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y_%B_%dth_%H-%M")  # Replace colon with hyphen
    dataset_folders = [name for name in os.listdir(user_folder) if os.path.isdir(os.path.join(user_folder, name))]
    next_dataset_number = len(dataset_folders) + 1
    dataset_folder_name = f"dataset_{next_dataset_number}_{formatted_datetime}"

    dataset_folder = os.path.join(user_folder, dataset_folder_name)
    os.makedirs(dataset_folder)

    # Keep track of which types of data have been written
    written_types = set()

    for key, value in player_data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    subfolder_path = os.path.join(dataset_folder, key)
                    os.makedirs(subfolder_path, exist_ok=True)
                    file_name = "data"
                    write_dict_to_csv(item, subfolder_path, file_name)
                    written_types.add(key)

    # Write each type of data to its own CSV file
    for key, value in player_data.items():
        if isinstance(value, dict):
            if key not in written_types:
                subfolder_path = os.path.join(dataset_folder, key)
                os.makedirs(subfolder_path, exist_ok=True)
                file_name = "data"
                write_dict_to_csv(value, subfolder_path, file_name)

    print(f"Player data for {username} has been saved.")
    # Save player tag and username to a CSV file
    save_player_tag_username(player_tag, username)


def save_player_tag_username(player_tag, username):
    with open("player_tags_usernames.csv", mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([player_tag, username])


def write_dict_to_csv(data, folder, file_name):
    csv_file_path = os.path.join(folder, f"{file_name}.csv")
    mode = 'a' if os.path.exists(csv_file_path) else 'w'
    with open(csv_file_path, mode=mode, newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if mode == 'w':
            writer.writerow(["Attribute", "Name", "Level", "Max Level", "Progress", "Target", "Icon URL"])
        write_dict_row(data, writer)

def write_dict_row(data, writer, prefix=""):
    for key, value in data.items():
        if isinstance(value, dict):
            write_dict_row(value, writer, f"{prefix}_{key}")
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                write_dict_row(item, writer, f"{prefix}_{key}_{idx}")
        else:
            writer.writerow([f"{prefix}_{key}", value])


if __name__ == "__main__":
    player_tag = input("Enter player tag: ")

    player_data = get_player_data(player_tag)

    if player_data:
        save_player_data(player_data, player_tag)
        print(f"Player data for {player_data.get('name', 'UnknownUser')} has been saved.")
    else:
        print("No player data available.")
