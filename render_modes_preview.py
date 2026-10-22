"""
render_modes_preview.py
Executes setup_lighting, then renders:
1. Day Mode (ENV_DAY_SUN_FILL ON, LIGHTS_NIGHT OFF, TVs OFF)
2. Night Mode with Lights (ENV_DAY_SUN_FILL OFF, LIGHTS_NIGHT ON, TVs ON)
3. Night Dark (ENV_DAY_SUN_FILL OFF, LIGHTS_NIGHT OFF, TVs OFF)
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
    # Also update view_layer
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
scene.cycles.samples = 48
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

iso_cam = bpy.data.objects.get("Isometric_Camera")
if iso_cam:
    scene.camera = iso_cam

# 1. Day Mode (Pure Daylight)
print(">>> Rendering 1: DAY MODE...")
set_collection_state("ENV_DAY_SUN_FILL", True)
set_collection_state("LIGHTS_NIGHT", False)
set_collection_state("TV_1.04_Active", False)
set_collection_state("TV_1.05_Active", False)
scene.render.filepath = os.path.join(artifact_dir, "test_mode_day.png")
bpy.ops.render.render(write_still=True)
print("Rendered test_mode_day.png!")

# 2. Night Mode with Lights
print(">>> Rendering 2: NIGHT MODE WITH LIGHTS...")
set_collection_state("ENV_DAY_SUN_FILL", False)
set_collection_state("LIGHTS_NIGHT", True)
set_collection_state("TV_1.04_Active", True)
set_collection_state("TV_1.05_Active", True)
scene.render.filepath = os.path.join(artifact_dir, "test_mode_night_lights.png")
bpy.ops.render.render(write_still=True)
print("Rendered test_mode_night_lights.png!")

# 3. Night Dark (No lights)
print(">>> Rendering 3: NIGHT DARK...")
set_collection_state("ENV_DAY_SUN_FILL", False)
set_collection_state("LIGHTS_NIGHT", False)
set_collection_state("TV_1.04_Active", False)
set_collection_state("TV_1.05_Active", False)
scene.render.filepath = os.path.join(artifact_dir, "test_mode_night_dark.png")
bpy.ops.render.render(write_still=True)
print("Rendered test_mode_night_dark.png!")

# Reset default state: Both ENV_DAY_SUN_FILL and LIGHTS_NIGHT visible=True, ready for user
set_collection_state("ENV_DAY_SUN_FILL", True)
set_collection_state("LIGHTS_NIGHT", True)
set_collection_state("TV_1.04_Active", True)
set_collection_state("TV_1.05_Active", True)

bpy.ops.wm.save_mainfile()
print(">>> Saved dum_pudorys.blend with default state!")
