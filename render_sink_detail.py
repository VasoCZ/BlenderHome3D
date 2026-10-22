import bpy
from mathutils import Vector
import os

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

artifact_dir = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6"

# Create a clean perspective camera looking at the sink and Upper_Oak_Door_4
cam_data = bpy.data.cameras.new("Cam_Sink_Detail")
cam_obj = bpy.data.objects.new("Cam_Sink_Detail", cam_data)
scene.collection.objects.link(cam_obj)

# Sink is around (3.32, 11.38, 0.90), Upper_Oak_Door_4 is at (3.33, 11.38, 1.70)
target = Vector((3.32, 11.38, 1.25))
# Place camera in front of it (around X=4.8, Y=9.8, Z=1.85) looking at sink
cam_obj.location = Vector((4.80, 9.80, 1.85))
cam_obj.rotation_euler = (target - cam_obj.location).to_track_quat('-Z', 'Y').to_euler()

scene.camera = cam_obj
scene.render.resolution_x = 960
scene.render.resolution_y = 640
scene.render.filepath = os.path.join(artifact_dir, "kitchen_sink_detail_view.png")

# Use daylight setup
bpy.ops.render.render(write_still=True)
print("Rendered kitchen_sink_detail_view.png!")

# Clean up
bpy.data.objects.remove(cam_obj)
bpy.data.cameras.remove(cam_data)

iso_cam = bpy.data.objects.get("Isometric_Camera")
if iso_cam:
    scene.camera = iso_cam
