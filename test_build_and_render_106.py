import bpy
import mathutils

# 1. Execute the build script
exec(open(r"C:\Users\Vaso\Antigravity\Project blender\build_room_106_furniture.py").read())

# 2. Setup Camera
cam_name = "Camera_Pokoj_106_Photo_Match"
cam_obj = bpy.data.objects.get(cam_name)
if not cam_obj:
    cam_data = bpy.data.cameras.new(cam_name)
    cam_obj = bpy.data.objects.new(cam_name, cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

cam_pos = mathutils.Vector((3.30, 1.75, 1.25))
cam_target = mathutils.Vector((0.65, 1.25, 0.65))

direction = cam_target - cam_pos
rot_quat = direction.to_track_quat('-Z', 'Y')

cam_obj.location = cam_pos
cam_obj.rotation_euler = rot_quat.to_euler()
cam_obj.data.lens = 19 # wide phone camera lens
cam_obj.data.sensor_width = 36
cam_obj.data.clip_start = 0.05
cam_obj.data.clip_end = 100.0

bpy.context.scene.camera = cam_obj
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.render.filepath = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\render_106_furniture_test3.png"

print("Rendering photo match test view 3 of room 1.06 furniture...")
bpy.ops.render.render(write_still=True)
print("Render completed: render_106_furniture_test3.png")
