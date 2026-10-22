"""
render_cinematic_views.py
Renders the master floorplans and targeted crops for the cinematic update:
1. dum_pudorys_overview.png (Day mode, Sun ON @ 5500K + Nishita sky, 2800K lights ON)
2. dum_pudorys_daylight_final.png (Pure daylight, Sun ON @ 5500K + Nishita sky, lights OFF)
3. dum_pudorys_night_overview.png (Night mode, Sun OFF, #02050D sky @ 0.08, 2800K lights ON)
4. dum_pudorys_night_dark.png (Pure dark night, Sun OFF, #02050D sky @ 0.08, lights OFF)
5. Targeted verification crops for paving, grass, terrace shadows, bedroom blinds, and night contrast.
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

    # A. Paving Texture Detail (Driveway paving stones with deep 3D joints)
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_cinematic_paving.png"), 120, 480, 800, 1060)

    # B. Grass Texture Detail (North-West garden lawn with dark green / olive tonal variation)
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_cinematic_grass.png"), 1450, 1850, 800, 1060)

    # C. Living Room & Terrace Sunlight & Dynamic Shadows
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_cinematic_terrace_shadows.png"), 520, 950, 280, 620)

    # D. Bedroom Bed Blinds Shadows
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_cinematic_bedroom_blinds.png"), 200, 620, 520, 890)

    # E. Night Warm 2800K Lights vs Cold #02050D Night Sky
    crop_box(night_overview_path, os.path.join(artifact_dir, "crop_cinematic_night_lights.png"), 480, 950, 260, 620)

    # F. Pure Night Exterior Darkness (#02050D subtle moonlight)
    crop_box(night_dark_path, os.path.join(artifact_dir, "crop_cinematic_night_dark.png"), 20, 480, 800, 1080)

    print(">>> All renders and crops completed successfully!")

if __name__ == '__main__':
    main()
