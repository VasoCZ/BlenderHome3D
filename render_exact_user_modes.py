"""
render_exact_user_modes.py
Tests and renders the native outliner toggles:
1. Master Day Overview (Sun_Fill.hide_render = False, Interior Lights ON, TVs OFF)
2. Pure Daylight Mode (Sun_Fill.hide_render = False, Interior Lights OFF, TVs OFF)
3. Master Night Overview (Sun_Fill.hide_render = True, Interior Lights ON, Exterior Soffits ON, TVs OFF)
4. Pure Dark Night (Sun_Fill.hide_render = True, Interior Lights OFF, TVs OFF)
5. Generates targeted high-res verification crops.
"""

import bpy
import numpy as np
import os
import shutil

def crop_box(img_path, out_path, x0, x1, y0, y1):
    im = bpy.data.images.load(img_path)
    w, h = im.size[0], im.size[1]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    px = np.array(im.pixels[:]).reshape((h, w, 4))
    cropped = px[y0:y1, x0:x1]
    res = bpy.data.images.new("Crop", width=cropped.shape[1], height=cropped.shape[0])
    res.pixels = cropped.flatten().tolist()
    res.filepath_raw = out_path
    res.file_format = 'PNG'
    res.save()
    bpy.data.images.remove(im)
    bpy.data.images.remove(res)
    print(f"  Saved crop: {os.path.basename(out_path)} ({cropped.shape[1]}x{cropped.shape[0]})")

def main():
    blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam

    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.device = 'GPU'
    except:
        pass
    scene.cycles.samples = 64
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    artifact_dir = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6"
    proj_dir = r"C:\Users\Vaso\Antigravity\Project blender"

    sun = bpy.data.objects.get("Sun_Fill")

    # -------------------------------------------------------------
    # 1. Master Daytime Floorplan Overview (Sun ON, Lights ON)
    # -------------------------------------------------------------
    print(">>> [1/4] Rendering Master Daytime Overview (dum_pudorys_overview.png)...")
    sun.hide_render = False
    sun.hide_viewport = False
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and ob.name.startswith('Light_1.') and 'tv' not in ob.name.lower() and 'Daylight' not in ob.name:
            ob.hide_render = False

    day_overview_path = os.path.join(proj_dir, "dum_pudorys_overview.png")
    scene.render.filepath = day_overview_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(day_overview_path, os.path.join(artifact_dir, "dum_pudorys_overview.png"))
    print("  Master Day Overview rendered successfully!")

    # -------------------------------------------------------------
    # 2. Pure Daylight Mode Floorplan (Sun ON, Lights OFF)
    # -------------------------------------------------------------
    print(">>> [2/4] Rendering Pure Daylight Floorplan (dum_pudorys_daylight_final.png)...")
    sun.hide_render = False
    sun.hide_viewport = False
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and ob.name.startswith('Light_1.') and 'Daylight' not in ob.name:
            ob.hide_render = True

    daylight_pure_path = os.path.join(proj_dir, "dum_pudorys_daylight_final.png")
    scene.render.filepath = daylight_pure_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(daylight_pure_path, os.path.join(artifact_dir, "dum_pudorys_daylight_final.png"))
    print("  Pure Daylight Floorplan rendered successfully!")

    # -------------------------------------------------------------
    # 3. Master Night Mode Floorplan (Sun OFF, Lights ON)
    # -------------------------------------------------------------
    print(">>> [3/4] Rendering Master Night Mode Floorplan (dum_pudorys_night_overview.png)...")
    sun.hide_render = True
    sun.hide_viewport = True
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and ob.name.startswith('Light_1.') and 'tv' not in ob.name.lower() and 'Daylight' not in ob.name:
            ob.hide_render = False

    night_overview_path = os.path.join(proj_dir, "dum_pudorys_night_overview.png")
    scene.render.filepath = night_overview_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(night_overview_path, os.path.join(artifact_dir, "dum_pudorys_night_overview.png"))
    print("  Master Night Overview rendered successfully!")

    # -------------------------------------------------------------
    # 4. Pure Dark Night Floorplan (Sun OFF, Lights OFF)
    # -------------------------------------------------------------
    print(">>> [4/4] Rendering Pure Dark Night Floorplan (dum_pudorys_night_dark.png)...")
    sun.hide_render = True
    sun.hide_viewport = True
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and (ob.name.startswith('Light_1.') or 'Daylight' in ob.name):
            ob.hide_render = True

    night_dark_path = os.path.join(proj_dir, "dum_pudorys_night_dark.png")
    scene.render.filepath = night_dark_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(night_dark_path, os.path.join(artifact_dir, "dum_pudorys_night_dark.png"))
    print("  Pure Dark Night Floorplan rendered successfully!")

    # Restore default blend state: Sun ON (Day mode default), interior lights ON, TVs OFF
    sun.hide_render = False
    sun.hide_viewport = False
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and ob.name.startswith('Light_1.') and 'tv' not in ob.name.lower() and 'Daylight' not in ob.name:
            ob.hide_render = False
            ob.hide_viewport = False
    bpy.ops.wm.save_mainfile()
    print("  Saved blend file with Sun ON (Day mode) default.")

    # -------------------------------------------------------------
    # 5. Generate Verification Crops
    # -------------------------------------------------------------
    print(">>> Generating verification crops...")

    # A. Day Exterior Paving Crop (Driveway & front lawn)
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_day_exterior_paving.png"), 20, 480, 800, 1080)

    # B. Day Bedroom Bed with Blinds Shadows
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_day_bedroom_blinds.png"), 200, 620, 520, 890)

    # C. Day Living Room Interior Light Visibility
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_day_living_light.png"), 680, 1050, 280, 600)

    # D. Pure Daylight Bathroom 1.10
    crop_box(daylight_pure_path, os.path.join(artifact_dir, "crop_day_bathroom_pure.png"), 1300, 1680, 580, 1010)

    # E. Night Exterior Dark with Blue Tint (Corner & Garden)
    crop_box(night_overview_path, os.path.join(artifact_dir, "crop_night_exterior_dark.png"), 20, 480, 800, 1080)

    # F. Night Living Room & Kitchen Glowing Lights
    crop_box(night_overview_path, os.path.join(artifact_dir, "crop_night_living_glowing.png"), 680, 1050, 280, 600)

    # G. Pure Dark Night (Full Darkness with Blue Tint)
    crop_box(night_dark_path, os.path.join(artifact_dir, "crop_night_pure_dark_corner.png"), 20, 480, 800, 1080)

    print(">>> All renders and crops completed successfully!")

if __name__ == '__main__':
    main()
