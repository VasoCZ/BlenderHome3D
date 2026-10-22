import bpy
import mathutils

cam_name = "Camera_Pokoj_106_Photo_Match"
cam_obj = bpy.data.objects.get(cam_name)
if not cam_obj:
    cam_data = bpy.data.cameras.new(cam_name)
    cam_obj = bpy.data.objects.new(cam_name, cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

# In room 1.06:
# Room bounds: X=[0.365, 4.395], Y=[0.365, 3.850]
# Southwest corner is at (0.365, 0.365).
# The photo is taken standing in the room, looking towards the Southwest corner (Desk on South wall, Kallax on West wall).
cam_pos = mathutils.Vector((2.8, 2.6, 1.35))
cam_target = mathutils.Vector((0.9, 0.9, 0.65))

direction = cam_target - cam_pos
rot_quat = direction.to_track_quat('-Z', 'Y')

cam_obj.location = cam_pos
cam_obj.rotation_euler = rot_quat.to_euler()
cam_obj.data.lens = 22 # wide angle smartphone lens
cam_obj.data.sensor_width = 36
cam_obj.data.clip_start = 0.05
cam_obj.data.clip_end = 100.0

bpy.context.scene.camera = cam_obj
bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 540
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 16
bpy.context.scene.render.filepath = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\test_camera_target_fixed.png"

bpy.ops.render.render(write_still=True)
print("Rendered test camera target fixed successfully!")
