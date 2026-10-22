"""
render_verifications_and_modes.py
Renders and generates all verification outputs:
1. Master Day Overview (dum_pudorys_overview.png)
2. Pure Daylight Mode (dum_pudorys_daylight_final.png)
3. Master Night Overview (dum_pudorys_night_overview.png)
4. Targeted crops for entrance lintel, window reveals, blinds shadows, bathroom, and exterior.
"""

import bpy
import numpy as np
import os
import shutil
import sys

sys.path.append(r"C:\Users\Vaso\Antigravity\Project blender")
from apply_lintel_shadows_and_lighting import set_mode

def crop_box(img_path, out_path, x0, x1, y0, y1):
    """Crops a region from an image given pixel coordinates in Blender coordinate system (Y=0 bottom)."""
    im = bpy.data.images.load(img_path)
    w, h = im.size[0], im.size[1]
    
    # Clamp to image dimensions
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

    # -------------------------------------------------------------
    # 1. Master Daytime Floorplan Overview
    # -------------------------------------------------------------
    print(">>> [1/3] Rendering Master Daytime Overview (dum_pudorys_overview.png)...")
    set_mode('day')
    day_overview_path = os.path.join(proj_dir, "dum_pudorys_overview.png")
    scene.render.filepath = day_overview_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(day_overview_path, os.path.join(artifact_dir, "dum_pudorys_overview.png"))
    print("  Master Day Overview rendered successfully!")

    # -------------------------------------------------------------
    # 2. Pure Daylight Mode Floorplan (All interior lights OFF)
    # -------------------------------------------------------------
    print(">>> [2/3] Rendering Pure Daylight Floorplan (dum_pudorys_daylight_final.png)...")
    set_mode('day')
    saved_energies = {}
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and ob.name != 'Sun_Fill' and 'Daylight' not in ob.name:
            saved_energies[ob.name] = ob.data.energy
            ob.data.energy = 0.0

    daylight_pure_path = os.path.join(proj_dir, "dum_pudorys_daylight_final.png")
    scene.render.filepath = daylight_pure_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(daylight_pure_path, os.path.join(artifact_dir, "dum_pudorys_daylight_final.png"))
    print("  Pure Daylight Floorplan rendered successfully!")

    # Restore interior lights
    for name, nrg in saved_energies.items():
        o = bpy.data.objects.get(name)
        if o and hasattr(o, 'data'):
            o.data.energy = nrg

    # -------------------------------------------------------------
    # 3. Master Night Mode Floorplan
    # -------------------------------------------------------------
    print(">>> [3/3] Rendering Master Night Mode Floorplan (dum_pudorys_night_overview.png)...")
    set_mode('night')

    night_overview_path = os.path.join(proj_dir, "dum_pudorys_night_overview.png")
    scene.render.filepath = night_overview_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(night_overview_path, os.path.join(artifact_dir, "dum_pudorys_night_overview.png"))
    print("  Master Night Overview rendered successfully!")

    # Restore Day mode in blend file as default
    set_mode('day')
    bpy.ops.wm.save_mainfile()
    print("  Saved blend file with Day mode default.")

    # -------------------------------------------------------------
    # 4. Generate Verification Crops from Day Overview & Pure Daylight
    # -------------------------------------------------------------
    print(">>> [4/4] Generating verification crops...")

    # A. Entrance Lintel Crop (from Day Overview)
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_entrance_lintel_fixed.png"), 270, 470, 930, 1080)

    # B. Patio Door Shadows Crop (from Day Overview)
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_patio_shadows_fixed.png"), 520, 830, 300, 620)

    # C. Bedroom Window Shadows Crop (from Day Overview)
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_bedroom_shadows_fixed.png"), 130, 340, 640, 960)

    # D. Bedroom Bed with Blinds Shadows Crop (from Pure Daylight)
    crop_box(daylight_pure_path, os.path.join(artifact_dir, "crop_bed_blinds_fixed.png"), 200, 620, 520, 890)

    # E. Technical Room Window Shadows Crop (from Day Overview)
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_tech_shadows_fixed.png"), 1240, 1490, 840, 1080)

    # F. Bathroom 1.10 Daylight Crop (from Pure Daylight)
    crop_box(daylight_pure_path, os.path.join(artifact_dir, "crop_bathroom_daylight_fixed.png"), 1300, 1680, 580, 1010)

    # G. Exterior Paving Crop (from Day Overview)
    crop_box(day_overview_path, os.path.join(artifact_dir, "crop_exterior_paving_fixed.png"), 20, 480, 800, 1080)

    print(">>> All verification renders and crops completed!")

if __name__ == '__main__':
    main()
