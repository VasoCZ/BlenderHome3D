import bpy
import math
import mathutils
from mathutils import Vector, Euler

# Import the builder
import sys
sys.path.append(r"C:\Users\Vaso\Antigravity\Project blender")
import build_mammotion_yuka

# Run the builder
build_mammotion_yuka.build_mammotion_yuka_system()

# Ensure ENV_DAY_SUN_FILL is visible for rendering
day_coll = bpy.data.collections.get("ENV_DAY_SUN_FILL")
if day_coll:
    day_coll.hide_render = False
    day_coll.hide_viewport = False

# Ensure Garden_Mammotion_Yuka is visible
yuka_coll = bpy.data.collections.get("Garden_Mammotion_Yuka")
if yuka_coll:
    yuka_coll.hide_render = False
    yuka_coll.hide_viewport = False

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 128
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.film_transparent = False

target = Vector((-1.15, 11.45, 0.18))

# Camera 1: Side Perspective matching yuka.jpg
cam1_data = bpy.data.cameras.new("Cam_Yuka_Side")
cam1_obj = bpy.data.objects.new("Cam_Yuka_Side", cam1_data)
bpy.context.scene.collection.objects.link(cam1_obj)
cam1_data.lens = 38
cam1_obj.location = Vector((-1.85, 10.30, 0.72))
dir1 = target - cam1_obj.location
rot_quat1 = dir1.to_track_quat('-Z', 'Y')
cam1_obj.rotation_euler = rot_quat1.to_euler()

scene.camera = cam1_obj
scene.render.filepath = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\render_yuka_side_view.png"
print("Rendering side view...")
bpy.ops.render.render(write_still=True)
print("Saved side view.")

# Camera 2: Rear Perspective matching yuka2.jpg
cam2_data = bpy.data.cameras.new("Cam_Yuka_Rear")
cam2_obj = bpy.data.objects.new("Cam_Yuka_Rear", cam2_data)
bpy.context.scene.collection.objects.link(cam2_obj)
cam2_data.lens = 42
cam2_obj.location = Vector((-2.45, 11.45, 0.65))
dir2 = target - cam2_obj.location
rot_quat2 = dir2.to_track_quat('-Z', 'Y')
cam2_obj.rotation_euler = rot_quat2.to_euler()

scene.camera = cam2_obj
scene.render.filepath = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\render_yuka_rear_view.png"
print("Rendering rear view...")
bpy.ops.render.render(write_still=True)
print("Saved rear view.")

# Clean up temporary inspection cameras
bpy.data.objects.remove(cam1_obj, do_unlink=True)
bpy.data.cameras.remove(cam1_data, do_unlink=True)
bpy.data.objects.remove(cam2_obj, do_unlink=True)
bpy.data.cameras.remove(cam2_data, do_unlink=True)

# Restore master camera
master_cam = bpy.data.objects.get("Camera") or bpy.data.objects.get("Camera_Pudorys")
if master_cam:
    scene.camera = master_cam

# Save blend file
bpy.ops.wm.save_mainfile(filepath=r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend")
print("Saved dum_pudorys.blend.")
