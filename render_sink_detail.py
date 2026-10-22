import bpy
from mathutils import Vector
import os

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

artifact_dir = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6"

cam_data = bpy.data.cameras.new("Cam_Sink_Detail")
cam_obj = bpy.data.objects.new("Cam_Sink_Detail", cam_data)
scene.collection.objects.link(cam_obj)

# Look at sink: X=3.32, Y=11.38, Z=1.15
target = Vector((3.32, 11.38, 1.15))
# Place camera looking from aisle towards sink and Upper_Oak_Door_4
cam_obj.location = Vector((4.50, 9.90, 1.75))
cam_obj.rotation_euler = (target - cam_obj.location).to_track_quat('-Z', 'Y').to_euler()

scene.camera = cam_obj
scene.render.resolution_x = 960
scene.render.resolution_y = 640
scene.render.filepath = os.path.join(artifact_dir, "kitchen_sink_detail_view.png")

scene.render.engine = 'CYCLES'
try:
    scene.cycles.device = 'GPU'
except:
    pass
scene.cycles.samples = 48

bpy.ops.render.render(write_still=True)
print("Rendered kitchen_sink_detail_view.png!")

bpy.data.objects.remove(cam_obj)
bpy.data.cameras.remove(cam_data)

iso_cam = bpy.data.objects.get("Isometric_Camera")
if iso_cam:
    scene.camera = iso_cam
