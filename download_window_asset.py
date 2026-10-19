import sys
import time
import os
import json
import requests
import bpy

from bl_ext.user_default.blenderkit import client_lib, global_vars, search, download, paths, utils

def main():
    print("Ensuring client process is alive...")
    if not client_lib.is_client_process_alive():
        print("Starting client...")
        client_lib.start_blenderkit_client()
        time.sleep(2.0)

    print("Client alive:", client_lib.is_client_process_alive())

    pref = bpy.context.preferences.addons['bl_ext.user_default.blenderkit'].preferences
    global_vars.PREFS = utils.get_preferences_as_dict()

    asset_base_id = "08d106b3-58d9-42d0-ae99-bce92d0b2667"
    params = {"asset_base_id": asset_base_id}
    print(f"Searching for asset: {asset_base_id}...")
    results = search.get_search_simple(params, page_size=1, max_results=1, api_key=pref.api_key)
    if not results:
        print("No results found!")
        return

    asset_data = search.parse_result(results[0])
    print(f"Found asset: {asset_data.get('name')}, id: {asset_data.get('id')}")

    prefs = utils.get_preferences_as_dict()
    prefs["resolution"] = "resolution_2K"
    prefs["scene_id"] = utils.get_scene_id()

    download_dirs = paths.get_download_dirs(asset_data["assetType"])
    print("Download dirs:", download_dirs)

    data = {
        "asset_data": asset_data,
        "PREFS": prefs,
        "progress": 0,
        "text": f"downloading {asset_data['name']}",
        "download_dirs": download_dirs,
        "downloaders": [],
        "model_location": [0.0, 0.0, 0.0],
        "model_rotation": [0.0, 0.0, 0.0],
        "replace": False,
        "cast_parent": False,
        "target_object": "",
        "target_collection": "",
        "material_target_slot": 0,
        "resolution": "resolution_2K",
        "started_at": time.monotonic(),
        "last_report_time": time.monotonic(),
    }

    resp = client_lib.asset_download(data)
    print("Download response:", resp)
    task_id = resp.get("task_id")
    if not task_id:
        print("Error: No task_id returned!")
        return

    print(f"Waiting for download task {task_id}...")
    app_id = os.getpid()
    finished = False
    for step in range(60):
        time.sleep(1.0)
        reports = client_lib.get_reports(app_id)
        for r in reports:
            if r.get("task_id") == task_id:
                status = r.get("status")
                progress = r.get("progress")
                msg = r.get("message")
                print(f"[{step}s] Progress: {progress}%, Status: {status}, Msg: {msg}")
                if status == "finished":
                    finished = True
                    print("Download complete!")
                    print("Result files:", r.get("data", {}).get("file_paths"))
                    break
                elif status == "error":
                    print("Download failed:", r)
                    return
        if finished:
            break
    else:
        print("Timed out waiting for download.")

if __name__ == "__main__":
    main()
