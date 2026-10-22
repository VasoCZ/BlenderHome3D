import bpy
import math
import mathutils

# Setup an isometric camera focused directly on room 1.06
cam_name = "Camera_1.06_Isometric"
cam_obj = bpy.data.objects.get(cam_name)
if not cam_obj:
    cam_data = bpy.data.cameras.new(cam_name)
    cam_obj = bpy.data.objects.new(cam_name, cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

cam_obj.data.type = 'ORTHO'
cam_obj.data.ortho_scale = 6.2 # frames room 1.06 perfectly
cam_obj.rotation_euler = (mathutils.Euler((math.radians(54.736), 0, math.radians(135)), 'XYZ')) # classic isometric

# Target center of room 1.06 is (2.38, 2.10, 1.0)
target = mathutils.Vector((2.38, 2.10, 0.75))
dist = 20.0
# Camera forward vector from Euler:
mw = cam_obj.matrix_world
forward = cam_obj.rotation_euler.to_quaternion() @ mathutils.Vector((0, 0, -1))
cam_obj.location = target - forward * dist

bpy.context.scene.camera = cam_obj
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 960
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.render.filepath = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\room_106_isometric_closeup.png"

print("Rendering room_106_isometric_closeup.png...")
bpy.ops.render.render(write_still=True)
print("Finished room_106_isometric_closeup.png!")
