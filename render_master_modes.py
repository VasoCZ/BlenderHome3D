"""
render_master_modes.py
Renders final high-quality master images:
1. dum_pudorys_daylight_master.png
2. dum_pudorys_night_master.png
3. dum_pudorys_night_dark_master.png
"""

import bpy
import os

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

artifact_dir = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6"

def set_collection_state(col_name, visible):
    col = bpy.data.collections.get(col_name)
    if col:
        col.hide_render = not visible
        col.hide_viewport = not visible
    def recurse(layer_col):
        if layer_col.collection.name == col_name:
            layer_col.exclude = not visible
            return True
        for child in layer_col.children:
            if recurse(child):
                return True
        return False
    recurse(bpy.context.view_layer.layer_collection)

scene.render.engine = 'CYCLES'
try:
    scene.cycles.device = 'GPU'
except:
    pass
scene.cycles.samples = 64
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

iso_cam = bpy.data.objects.get("Isometric_Camera")
if iso_cam:
    scene.camera = iso_cam

# 1. Master Day Mode
print(">>> Rendering 1: MASTER DAY MODE...")
set_collection_state("ENV_DAY_SUN_FILL", True)
set_collection_state("LIGHTS_NIGHT", False)
set_collection_state("TV_1.04_Active", False)
set_collection_state("TV_1.05_Active", False)
scene.render.filepath = os.path.join(artifact_dir, "dum_pudorys_daylight_master.png")
bpy.ops.render.render(write_still=True)
print("Rendered dum_pudorys_daylight_master.png!")

# 2. Master Night Mode
print(">>> Rendering 2: MASTER NIGHT MODE WITH LIGHTS...")
set_collection_state("ENV_DAY_SUN_FILL", False)
set_collection_state("LIGHTS_NIGHT", True)
set_collection_state("TV_1.04_Active", True)
set_collection_state("TV_1.05_Active", True)
scene.render.filepath = os.path.join(artifact_dir, "dum_pudorys_night_master.png")
bpy.ops.render.render(write_still=True)
print("Rendered dum_pudorys_night_master.png!")

# 3. Master Night Dark
print(">>> Rendering 3: MASTER NIGHT DARK...")
set_collection_state("ENV_DAY_SUN_FILL", False)
set_collection_state("LIGHTS_NIGHT", False)
set_collection_state("TV_1.04_Active", False)
set_collection_state("TV_1.05_Active", False)
scene.render.filepath = os.path.join(artifact_dir, "dum_pudorys_night_dark_master.png")
bpy.ops.render.render(write_still=True)
print("Rendered dum_pudorys_night_dark_master.png!")

# Reset default open state in Blend file:
# Keep all collections active (visible=True, unhidden) so user sees everything loaded and can toggle off with one click
set_collection_state("ENV_DAY_SUN_FILL", True)
set_collection_state("LIGHTS_NIGHT", True)
set_collection_state("TV_1.04_Active", True)
set_collection_state("TV_1.05_Active", True)

bpy.ops.wm.save_mainfile()
print(">>> Saved dum_pudorys.blend with active collections ready for Outliner toggling!")
