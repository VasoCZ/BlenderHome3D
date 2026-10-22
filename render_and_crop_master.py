"""
render_and_crop_master.py
Renders updated master images and generates inspection crops:
1. dum_pudorys_daylight_master.png
2. dum_pudorys_night_master.png
3. Inspection crops:
   - crop_kitchen_new_day.png (shows sink under Upper_Oak_Door_4, oven handle, hob)
   - crop_oven_handle_new.png (close-up of oven handle matching control panel)
   - crop_bedroom_tv_new.png (bedroom TV area light shape in night mode)
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
day_path = os.path.join(artifact_dir, "dum_pudorys_daylight_master.png")
scene.render.filepath = day_path
bpy.ops.render.render(write_still=True)
print("Rendered dum_pudorys_daylight_master.png!")

# 2. Master Night Mode
print(">>> Rendering 2: MASTER NIGHT MODE WITH LIGHTS...")
set_collection_state("ENV_DAY_SUN_FILL", False)
set_collection_state("LIGHTS_NIGHT", True)
set_collection_state("TV_1.04_Active", True)
set_collection_state("TV_1.05_Active", True)
night_path = os.path.join(artifact_dir, "dum_pudorys_night_master.png")
scene.render.filepath = night_path
bpy.ops.render.render(write_still=True)
print("Rendered dum_pudorys_night_master.png!")

# Reset default state for user:
set_collection_state("ENV_DAY_SUN_FILL", True)
set_collection_state("LIGHTS_NIGHT", True)
set_collection_state("TV_1.04_Active", True)
set_collection_state("TV_1.05_Active", True)
bpy.ops.wm.save_mainfile()
print("Saved blendfile!")

# 3. Crops
def save_crop(src_path, dst_path, x0, y0, w, h):
    src = bpy.data.images.load(src_path)
    sw, sh = src.size
    dst = bpy.data.images.new('Crop', w, h)
    src_pixels = list(src.pixels)
    crop_pixels = [0.0] * (w * h * 4)
    for row in range(h):
        sy = y0 + row
        if sy >= sh: break
        src_start = (sy * sw + x0) * 4
        dst_start = (row * w) * 4
        crop_pixels[dst_start : dst_start + w*4] = src_pixels[src_start : src_start + w*4]
    dst.pixels = crop_pixels
    dst.filepath_raw = dst_path
    dst.file_format = 'PNG'
    dst.save()
    bpy.data.images.remove(dst)
    bpy.data.images.remove(src)

# Kitchen in Daylight:
save_crop(day_path, os.path.join(artifact_dir, "crop_kitchen_new_day.png"), 1150, 480, 450, 360)
# Oven handle close-up in Daylight:
save_crop(day_path, os.path.join(artifact_dir, "crop_oven_handle_new.png"), 1130, 630, 240, 220)
# Bedroom TV in Night:
save_crop(night_path, os.path.join(artifact_dir, "crop_bedroom_tv_new.png"), 150, 520, 420, 350)

print(">>> Finished all renders and crops successfully!")
