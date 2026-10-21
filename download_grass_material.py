import sys
import time
import os
import json
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

    asset_base_id = "b7ed2066-ee2d-4fa4-94e5-a162c265c854"
    params = {"asset_base_id": asset_base_id}
    print(f"Searching for asset: {asset_base_id}...")
    results = search.get_search_simple(params, page_size=1, max_results=1, api_key=pref.api_key)
    if not results:
        print("No results found with get_search_simple, trying search_assets...")
        # fallback search
        import requests
        url = f"https://www.blenderkit.com/api/v1/search/?query={asset_base_id}&addon_version=1.0.0"
        r = requests.get(url)
        print("Direct API status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
        
    if not results:
        print("Error: Asset not found on BlenderKit!")
        return

    asset_data = search.parse_result(results[0])
    print(f"Found asset: {asset_data.get('name')}, type: {asset_data.get('assetType')}, id: {asset_data.get('id')}")

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
    for step in range(120):
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
                    file_paths = r.get("data", {}).get("file_paths", [])
                    print("Result files:", file_paths)
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
