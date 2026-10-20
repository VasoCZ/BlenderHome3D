import bpy
from mathutils import Vector
import os

base_dir = r"C:\Users\Vaso\Antigravity\Project blender"
blend_path = os.path.join(base_dir, "dum_pudorys.blend")

bpy.ops.wm.open_mainfile(filepath=blend_path)

def setup_camera_lookat(name, loc, target, focal_length=20):
    cam = bpy.data.objects.get(name)
    if not cam:
        cam_data = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cam_data)
        bpy.context.scene.collection.objects.link(cam)
    
    cam.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = focal_length
    cam.data.clip_start = 0.05
    return cam

scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'PNG'

# 1. WC Interior: from east side of WC (X=1.45, Y=7.30, Z=1.45) looking towards West-North corner (X=0.365, Y=8.10, Z=0.80)
cam1 = setup_camera_lookat("Cam_WC_Inside", (1.45, 7.30, 1.45), (0.365, 7.90, 0.70), focal_length=18)
scene.camera = cam1
scene.render.filepath = os.path.join(base_dir, "wc_interior_view.png")
bpy.ops.render.render(write_still=True)
print("Rendered wc_interior_view.png")

# 2. WC from corridor looking through open door
cam2 = setup_camera_lookat("Cam_WC_Door", (2.30, 7.60, 1.40), (0.365, 7.63, 0.80), focal_length=24)
scene.camera = cam2
scene.render.filepath = os.path.join(base_dir, "wc_entrance_view.png")
bpy.ops.render.render(write_still=True)
print("Rendered wc_entrance_view.png")

# 3. Tech room interior: showing 15cm soklik and white plaster above
cam3 = setup_camera_lookat("Cam_Tech", (1.45, 8.40, 1.40), (0.365, 9.40, 0.60), focal_length=18)
scene.camera = cam3
scene.render.filepath = os.path.join(base_dir, "tech_interior_view.png")
bpy.ops.render.render(write_still=True)
print("Rendered tech_interior_view.png")

# 4. Zadveri detail: showing 15cm soklik
cam4 = setup_camera_lookat("Cam_Zadveri", (5.70, 0.70, 1.40), (3.775, 2.00, 0.50), focal_length=20)
scene.camera = cam4
scene.render.filepath = os.path.join(base_dir, "zadveri_soklik_view.png")
bpy.ops.render.render(write_still=True)
print("Rendered zadveri_soklik_view.png")

print("All targeted verification views rendered successfully.")
