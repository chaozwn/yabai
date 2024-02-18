# TODO
import subprocess
import json
import os


def run_command(command):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        shell=True,
        text=True,
    )
    try:
        result_output_json = json.loads(result.stdout)
    except json.JSONDecodeError:
        result_output_json = {}
    return result_output_json


def init():
    # 判断/tmp/yabai_status.json是否存在, 如果存在读取文件
    if os.path.exists("/tmp/yabai_status.json"):
        with open("/tmp/yabai_status.json", "r") as f:
            try:
                yabai_status = json.load(f)
            except json.JSONDecodeError:
                yabai_status = {}
            return yabai_status
    else:
        return {}


def find_space_by_index(spaces, index):
    for space in spaces:
        if space["index"] == index:
            return space

def find_window_by_id(windows, id):
    for window in windows:
        if window["id"] == id:
            return window

yabai_status = init()
# 查询displays
displays = run_command("yabai -m query --displays")
spaces = run_command("yabai -m query --spaces")
windows = run_command("yabai -m query --windows")
for display in displays:
    display_index = display["index"]
    # 处理对应的spaces
    display_space_indexes = display["spaces"]
    spaces_dict = {
        f'space_{space["index"]}': space
        for index in display_space_indexes
        for space in [find_space_by_index(spaces, index)]
    }
    for _, space in spaces_dict.items():
        display_space_window_indexes = space['windows']
        windows_dict = {
            f'window_{window["id"]}': window
            for index in display_space_window_indexes
            for window in [find_window_by_id(windows, index)]
        }
        space["windows"] = windows_dict

    display["spaces"] = spaces_dict
    yabai_status[f"display_{display_index}"] = display

# 覆盖/tmp/yabai_status.json
with open("/tmp/yabai_status.json", "w") as f:
    json.dump(yabai_status, f, indent=4)
